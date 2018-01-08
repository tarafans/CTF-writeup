#include <Common/drv_common.h>
#include <Common/kernel/KernelModule.hpp>

#include <memory>

//---------------------------
//----   ENTRY PIONT   ------
//---------------------------

#include "0ctfCore.hpp"

NTSTATUS 
DummyIoctlNot(
	__inout DEVICE_OBJECT*,
	__inout IRP*
	)
{
	return STATUS_NOT_SUPPORTED;
}
NTSTATUS 
DummyIoctlOK(
	__inout DEVICE_OBJECT*,
	__inout IRP*
	)
{
	return STATUS_SUCCESS;
}

NTSTATUS
Create(
	__inout DEVICE_OBJECT* device,
	__inout IRP* irp
	)
{
	return C0opsCore::Push(device, irp);
}

NTSTATUS
Close(
	__inout DEVICE_OBJECT* device,
	__inout IRP*
	)
{
	return C0opsCore::Pop(device);
}

NTSTATUS 
Ioctl(
	__inout DEVICE_OBJECT* device,
	__inout IRP* irp
	)
{
	return C0opsCore::Ioctl(device, irp);
}

NTSTATUS 
Set(
	__inout DEVICE_OBJECT* device,
	__inout IRP* irp
	)
{
	return C0opsCore::Set(device, irp);
}

NTSTATUS 
Query(
	__inout DEVICE_OBJECT* device,
	__inout IRP* irp
	)
{
	return C0opsCore::Query(device, irp);
}

NTSTATUS 
Read(
	__inout DEVICE_OBJECT* device,
	__inout IRP* irp
	)
{
	return C0opsCore::Read(device, irp);
}

NTSTATUS 
Write(
	__inout DEVICE_OBJECT* device,
	__inout IRP* irp
	)
{
	return C0opsCore::Write(device, irp);
}

__checkReturn
bool
drv_main()
{
	auto driver = CKernelModule::DriverObject();
    PDEVICE_OBJECT pDeviceObject = NULL;


	UNICODE_STRING driver_name = { 0 };
	RtlInitUnicodeString(&driver_name, L"\\Device\\0opsCore");
		
	DEVICE_OBJECT* device = nullptr;
	auto status = IoCreateDevice(driver, 0, &driver_name, FILE_DEVICE_UNKNOWN, FILE_DEVICE_SECURE_OPEN, FALSE, &device);
	if (!NT_SUCCESS(status))
		return false;

	UNICODE_STRING dos_name = { 0 };
	RtlInitUnicodeString(&dos_name, L"\\DosDevices\\0opsCore");
	status = IoCreateSymbolicLink(&dos_name, &driver_name);
	if (!NT_SUCCESS(status))
		return false;

	for (size_t i = 0; i< IRP_MJ_MAXIMUM_FUNCTION; i++)
		driver->MajorFunction[i] = DummyIoctlNot;

	driver->MajorFunction[IRP_MJ_CLOSE] = Close;
	driver->MajorFunction[IRP_MJ_CREATE] = Create;
	driver->MajorFunction[IRP_MJ_READ] = Read;
	driver->MajorFunction[IRP_MJ_WRITE] = Write;
	driver->MajorFunction[IRP_MJ_DEVICE_CONTROL] = Ioctl;
	driver->MajorFunction[IRP_MJ_QUERY_INFORMATION] = Query;
	driver->MajorFunction[IRP_MJ_SET_INFORMATION] = Set;

	device->Flags |= DO_BUFFERED_IO;
	device->Flags &= (~DO_DEVICE_INITIALIZING);

	printf("0hello cpp driver");

	return true;
}
