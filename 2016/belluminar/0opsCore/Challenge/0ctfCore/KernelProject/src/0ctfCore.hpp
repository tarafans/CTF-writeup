#pragma once

#include <boost/intrusive/rbtree.hpp>
#include <Common/utils/LockTree.h>
#include <memory>

#include <wdm.h>

struct HEAD :
	public avl_set_base_hook<>,
	public list_base_hook<>,
	public CComparableId<HANDLE>
{
	HEAD(
		__in HANDLE threadId,
		__in DEVICE_OBJECT* device = nullptr
		) :	CComparableId(threadId),
			Device(device)
	{
	}
	DEVICE_OBJECT* Device;
};

#define IOCTL_HOOKER_CODE CTL_CODE(FILE_DEVICE_UNKNOWN, 0x802, METHOD_BUFFERED, FILE_WRITE_DATA)
#define FileBasicInfo 4

auto ops_assert = [](bool expression) { if (!expression) KeBugCheck(0x0666); };

class C0opsCore :
	public CLockedNode<DEVICE_OBJECT*>
{
	static
	CFastAvl<C0opsCore> m_cores;
	static
	CFastAvl<HEAD> m_heads;

	size_t m_flagMaxLen;
	size_t m_keyOne;

	char m_keyXor[0x10];//intentionally unitialized ... more bugs more fun

	size_t* m_bitmap;

	static const size_t m_sMaLen = 0x1000;

public:
	C0opsCore(
		__in DEVICE_OBJECT* device
		) : CLockedNode(device),
			m_flagMaxLen(m_sMaLen),
			m_keyOne(std::rand())
	{
		m_bitmap = static_cast<size_t*>(ExAllocatePool(PagedPoolSession, m_flagMaxLen));

		for (size_t i = 0; i < sizeof(m_keyOne); i++)
			reinterpret_cast<char*>(&m_keyOne)[i] = std::rand() % 0xFF;

		//in 3 level flag stage this should be commented out ...
		for (size_t i = 0; i < sizeof(m_keyXor); i++)
			m_keyXor[i] = std::rand() % 0xFF;
	}
	~C0opsCore()
	{
		ExFreePool(m_bitmap);//delete, but not nullify it!
	}
	static
	__checkReturn
	NTSTATUS
	Push(
		__in DEVICE_OBJECT* device,
		__in IRP*
		)
	{
		std::unique_ptr<C0opsCore> core(new C0opsCore(device));
		if (!core)
			return STATUS_UNSUCCESSFUL;

		auto head_it = MyHead(device);
		if (!head_it)
			return STATUS_UNSUCCESSFUL;
		
		auto head = FindCore(head_it->Device);
		if (!head)
			head = core.get();

		//bad lock here ...
		auto lock = m_heads.ReadWriteLockHolder();
		
		//race, if head then parrent can be deleted meanwhile ..
		//to prolong race insert many cores 
		if (!core->m_bitmap)
			return STATUS_UNSUCCESSFUL;

		//while ((m_cores.end() != m_cores.find(*core)))//wait for race by default ...
		for (size_t j = 0; j < m_sMaLen; j++)
			for (size_t i = 0; i < m_sMaLen; i++)
				reinterpret_cast<char*>(core->m_bitmap)[i] ^= std::rand() % 0xFF;

		if (m_cores.end() != m_cores.find(*core))
			return STATUS_UNSUCCESSFUL;

		if (!m_cores.insert_unique(*core).second)
			return STATUS_UNSUCCESSFUL;

		std::swap(head->m_bitmap, core->m_bitmap);

		core.release();
		return STATUS_SUCCESS;
	}
	static
	__checkReturn
	NTSTATUS
	Pop(
		__in DEVICE_OBJECT* device
		)
	{
		std::unique_ptr<C0opsCore> scoped_core;
		{
			auto lock = m_cores.ReadWriteLockHolder();
			auto core = m_cores.find(device);
			if (m_cores.end() == core)
				return STATUS_SUCCESS;
			m_cores.erase(core);
			scoped_core.reset(&*core);
		}//delete outside of lock .. sidefect, prolong race time ...
		return STATUS_SUCCESS;
	}
	static
	__checkReturn
	NTSTATUS
	Ioctl(
		__in DEVICE_OBJECT* device,
		__in IRP* irp
		)
	{
		NTSTATUS status = STATUS_UNSUCCESSFUL;
		{
			auto lock = m_cores.ReadWriteLockHolder();
			auto core = FindCore(device);
			if (!core)
				return STATUS_UNSUCCESSFUL;

			status = core->Ioctl(irp);
		}
		return RequestFinished(status, irp);
	}
	static
	__checkReturn
	NTSTATUS
	Read(
		__in DEVICE_OBJECT* device,
		__in IRP* irp
		)
	{
		NTSTATUS status = STATUS_UNSUCCESSFUL;
		{
			auto lock = m_cores.ReadWriteLockHolder();
			auto core = FindCore(device);
			if (!core)
				return STATUS_UNSUCCESSFUL;

			status = core->Read(irp);
		}
		return RequestFinished(status, irp);
	}
	static
	__checkReturn
	NTSTATUS
	Write(
		__in DEVICE_OBJECT* device,
		__in IRP* irp
		)
	{
		NTSTATUS status = STATUS_UNSUCCESSFUL;
		{
			auto lock = m_cores.ReadWriteLockHolder();
			auto core = FindCore(device);
			if (!core)
				return STATUS_UNSUCCESSFUL;

			status = core->Write(irp);
		}
		return RequestFinished(status, irp);
	}
	static
	__checkReturn
	NTSTATUS
	Set(
		__in DEVICE_OBJECT* device,
		__in IRP* irp
		)
	{
		NTSTATUS status = STATUS_UNSUCCESSFUL;
		{
			auto lock = m_cores.ReadWriteLockHolder();
			auto core = FindCore(device);
			if (!core)
				return STATUS_UNSUCCESSFUL;

			status = core->Set(irp);
		}
		return RequestFinished(status, irp);
	}
	static
	__checkReturn
	NTSTATUS
	Query(
		__in DEVICE_OBJECT* device,
		__in IRP* irp
		)
	{
		NTSTATUS status = STATUS_UNSUCCESSFUL;
		{
			auto lock = m_cores.ReadWriteLockHolder();
			auto core = FindCore(device);
			if (!core)
				return STATUS_UNSUCCESSFUL;

			status = core->Query(irp);
		}
		return RequestFinished(status, irp);
	}
protected:
	static
	NTSTATUS
	RequestFinished(
		__in NTSTATUS status,
		__inout IRP* irp
		)
	{
		//if (!NT_SUCCESS(status))
		//	return status;

		irp->IoStatus.Status = status;

		IoCompleteRequest(irp, IO_NO_INCREMENT);
		return status;
	}
	__checkReturn
	NTSTATUS
	Ioctl(
		__in IRP* irp
		)
	{
		auto io_stack = IoGetCurrentIrpStackLocation(irp);
		if (!io_stack)
			return STATUS_NOT_SUPPORTED;

		auto iocode = io_stack->Parameters.DeviceIoControl.IoControlCode;

		switch (iocode)
		{
		case IOCTL_HOOKER_CODE:
			break;
		default:
			return STATUS_NOT_SUPPORTED;
		}

		auto buf = static_cast<char*>(irp->AssociatedIrp.SystemBuffer);
		if (!buf)
			return STATUS_UNSUCCESSFUL;

		auto len = io_stack->Parameters.DeviceIoControl.InputBufferLength;

		ops_assert(m_flagMaxLen >= len);//lost assert, allows to dump out image

		if (m_flagMaxLen != len)
			return STATUS_UNSUCCESSFUL;
		
		for (size_t i = 0; i < len; i++)
			m_keyXor[i % _countof(m_keyXor)] += buf[i];

		return STATUS_SUCCESS;
	}
	__checkReturn
	NTSTATUS
	Read(
		__in IRP* irp
		)
	{
		auto io_stack = IoGetCurrentIrpStackLocation(irp);
		if (!io_stack)
			return STATUS_NOT_SUPPORTED;

		auto len = io_stack->Parameters.Read.Length;
		if (m_flagMaxLen < len)
			return STATUS_NOT_SUPPORTED;

		auto buf = static_cast<char*>(irp->AssociatedIrp.SystemBuffer);
		if (!buf)
			return STATUS_UNSUCCESSFUL;

		memcpy(buf, m_bitmap, len);
		irp->IoStatus.Information = len;
		return STATUS_SUCCESS;
	}
	__checkReturn
	NTSTATUS
	Write(
		__in IRP* irp
		)
	{
		auto io_stack = IoGetCurrentIrpStackLocation(irp);
		if (!io_stack)
			return STATUS_NOT_SUPPORTED;

		auto len = io_stack->Parameters.Write.Length;
		if (m_flagMaxLen < len)
			return STATUS_NOT_SUPPORTED;

		auto buf = static_cast<char*>(irp->AssociatedIrp.SystemBuffer);
		if (!buf)
			return STATUS_UNSUCCESSFUL;

		for (size_t i = 0; i < len / sizeof(char); i++)
			(reinterpret_cast<char*>(m_bitmap))[i] = buf[i] ^ m_keyXor[i % _countof(m_keyXor)];

		irp->IoStatus.Information = (len / sizeof(char)) * sizeof(char);
		return STATUS_SUCCESS;
	}
	__checkReturn
	NTSTATUS
	Set(
		__in IRP* irp
		)
	{
		auto io_stack = IoGetCurrentIrpStackLocation(irp);
		if (!io_stack)
			return STATUS_NOT_SUPPORTED;

		if (FileBasicInfo != io_stack->Parameters.SetFile.FileInformationClass)
			return STATUS_NOT_SUPPORTED;

		if (io_stack->Parameters.SetFile.Length < sizeof(size_t))
			return STATUS_UNSUCCESSFUL;

		auto buf = static_cast<size_t*>(irp->AssociatedIrp.SystemBuffer);
		if (!buf)
			return STATUS_UNSUCCESSFUL;

		auto len = *buf;

		if (m_flagMaxLen < len)
			return STATUS_NOT_SUPPORTED;

		m_flagMaxLen = len;

		irp->IoStatus.Information = sizeof(len);
		return STATUS_SUCCESS;
	}
	__checkReturn
	NTSTATUS
	Query(
		__in IRP* irp
		)
	{
		auto io_stack = IoGetCurrentIrpStackLocation(irp);
		if (!io_stack)
			return STATUS_NOT_SUPPORTED;

		if (FileBasicInfo != io_stack->Parameters.QueryFile.FileInformationClass)
			return STATUS_NOT_SUPPORTED;

		auto len = io_stack->Parameters.QueryFile.Length;
		if (m_flagMaxLen < len)
			return STATUS_UNSUCCESSFUL;

		auto buf = static_cast<size_t*>(irp->AssociatedIrp.SystemBuffer) + 1;
		if (!buf)
			return STATUS_UNSUCCESSFUL;

		//static const char flag[] = "fr0mzer0toh3r0w1thctfpwnfl4g";
		//if (len < sizeof(flag) + sizeof(size_t))
			//return STATUS_UNSUCCESSFUL;

		buf[-1] = m_flagMaxLen;
		//memcpy(buf, flag, sizeof(flag));
		for (size_t i = 0; i < (/*sizeof(flag)*/ len / sizeof(m_keyOne)); i++)
			buf[i] ^= m_keyOne;

		irp->IoStatus.Information = len;// sizeof(flag);
		return STATUS_SUCCESS;
	}
	
private:
	static
	__checkReturn
	C0opsCore*
	FindCore(
		__in DEVICE_OBJECT* device
		)
	{
		auto core = m_cores.find(device);
		if (m_cores.end() == core)
			return nullptr;
		return &*core;
	}
	static
	__checkReturn
	HEAD*
	MyHead(
		__in DEVICE_OBJECT* device
		)
	{
		auto lock = m_heads.ReadWriteLockHolder();
		auto head_it = m_heads.find(PsGetCurrentThreadId());
		if (m_heads.end() != head_it)
			return &*head_it;

		auto head = new HEAD(PsGetCurrentThreadId(), device);
		if (!head)
			return nullptr;

		m_heads.insert_unique(*head);
		return head;
	}
};

__declspec(selectany)
CFastAvl<C0opsCore>
C0opsCore::m_cores;

__declspec(selectany)
CFastAvl<HEAD>
C0opsCore::m_heads;
