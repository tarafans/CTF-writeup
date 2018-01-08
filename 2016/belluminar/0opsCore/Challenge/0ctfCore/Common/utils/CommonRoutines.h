#pragma once

#include "../drv_common.h"
#include "../kernel/VirtualMemory.h"

namespace CommonUser
{
	void
	ResolveImageName(
		__in_ecount(len) const WCHAR* fullImagePath,
		__in size_t len,
		__out UNICODE_STRING* imageName
		);

	__checkReturn
	bool
	IsUserModeAddress(
		__in const void* addr
		);

	__checkReturn
	bool
	IsUserModeAddress(
		__in size_t addr
		);

	void 
	ReadStringA(
		__in const void* addr,
		__inout_ecount(len) char* buff,
		__in size_t len
		);

	void 
	ReadStringW(
		__in const void* addr,
		__inout_ecount(len) wchar_t* buff,
		__in size_t len
		);

	__checkReturn
	bool
	MdlReadMemory(
		__in const void* addr,
		__inout_bcount(size) void* buff,
		__in size_t size
		);

	
//////////////////////////////////////////////////////////////////////////
/// TEMPLATED METHODS
//////////////////////////////////////////////////////////////////////////

	_IRQL_requires_max_(APC_LEVEL)
	template<typename TYPE>
	void 
	ReadString(
		__in const void* addr, 
		__inout_ecount(len) TYPE* buff,
		__in size_t len
		)
	{
		ReadMemory<TYPE>(addr, buff, len - 1);
		buff[len - 1] = 0;
	}

	//for DISPATCH_LEVEL use directly MDL !  VirtualMemory
	_IRQL_requires_max_(APC_LEVEL)
	template<typename TYPE>
	__checkReturn
	bool
	ReadMemory(
		__in const void* addr,
		__in_ecount(len) TYPE* buff,
		__in size_t len = 1
		)
	{
		if (!len)
			return false;

		size_t size = len * sizeof(TYPE);
		__try
		{
			ProbeForRead((volatile void*)addr, size, sizeof(unsigned char));
			memcpy(buff, addr, size);
			return true;
		}
		__except (EXCEPTION_EXECUTE_HANDLER)
		{
			MdlReadMemory(addr, buff, size);
		}
		return true;
	}

	_IRQL_requires_max_(APC_LEVEL)
	template<typename TYPE>
	__checkReturn
	TYPE
	ReadType(
		__in const void* addr
		)
	{
		TYPE obj;
		if (!ReadMemory<TYPE>(addr, &obj))
			return NULL;//force to read just simple types!
		return obj;
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
		);

	//for DISPATCH_LEVEL use directly MDL !  VirtualMemory
	_IRQL_requires_max_(APC_LEVEL)
	template<typename TYPE>
	__checkReturn
	bool
	ReadMemory(
		__in const void* addr,
		__in_ecount(len) TYPE* buff,
		__in size_t len = 1
		)
	{
		size_t size = len * sizeof(TYPE);
		__try
		{
			memcpy(buff, addr, size);
			return true;
		}
		__except (EXCEPTION_EXECUTE_HANDLER)
		{
			MdlReadMemory(addr, buff, size);
		}
		return true;
	}

	_IRQL_requires_max_(APC_LEVEL)
	template<typename TYPE>
	__checkReturn
	TYPE
	ReadType(
		__in const void* addr
		)
	{
		TYPE obj;
		if (!ReadMemory<TYPE>(addr, &obj))
			return NULL;//force to read just simple types!
		return obj;
	}
}