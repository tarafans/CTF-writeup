#include "../drv_common.h"
#include "CommonRoutines.h"
#include "../kernel/IRQL.hpp"

#include <string>

namespace CommonUser
{
	void
	ResolveImageName(
		__in_ecount(len) const WCHAR* fullImagePath,
		__in size_t len,
		__out UNICODE_STRING* imageName
		)
	{
		imageName->Buffer = const_cast<WCHAR*>(fullImagePath + (1 + std::wstring(fullImagePath).find_last_of(L"\\", len)));
		imageName->Length = static_cast<USHORT>((len - (imageName->Buffer - fullImagePath)) * sizeof(fullImagePath[0]));
		imageName->MaximumLength = imageName->Length + sizeof(fullImagePath[0]);
	}

	__checkReturn
	bool
	IsUserModeAddress(
		__in const void* addr
		)
	{
		return (addr <= MmHighestUserAddress);
	}

	__checkReturn
	bool
	IsUserModeAddress(
		__in size_t addr
		)
	{
		return IsUserModeAddress(reinterpret_cast<void*>(addr));
	}

	void
	ReadStringA(
		__in const void* addr, 
		__inout_ecount(len) char* buff, 
		__in size_t len
		)
	{
		ReadString<char>(addr, buff, len);
	}

	void 
	ReadStringW(
		__in const void* addr, 
		__inout_ecount(len) wchar_t* buff, 
		__in size_t len
		)
	{
		ReadString<wchar_t>(addr, buff, len);
	}

	__checkReturn
	bool
	MdlReadMemory(
		__in const void* addr,
		__inout_bcount(size) void* buff,
		__in size_t size
		)
	{
		CVirtMem vmem(addr, size);
		const void* mem = vmem.ReadPtrUser();
		if (!mem)
			return false;
		memcpy(buff, mem, size);
		return true;
	}
}

namespace CommonKernel
{
	__checkReturn
	bool
	MdlReadMemory(
		__in const void* addr, 
		__inout_bcount(size) void* buff, 
		__in size_t size
		)
	{
		CVirtMem vmem(addr, size);
		const void* mem = vmem.ReadPtr();
		if (!mem)
			return false;
		memcpy(buff, mem, size);
		return true;
	}
}
