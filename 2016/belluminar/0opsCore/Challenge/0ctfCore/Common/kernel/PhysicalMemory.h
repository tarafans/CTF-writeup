#pragma once

#include "../drv_common.h"

class CMmMap
{
public:
	CMmMap(
		__in ULONG_PTR address,
		__in size_t size
		);

	CMmMap(
		__in const void* address,
		__in size_t size
		);

	CMmMap(
		__in const PHYSICAL_ADDRESS& address, 
		__in size_t size
		);

	~CMmMap();

	void* GetVirtualAddress();

protected:
	void Init(
		__in ULONG_PTR address,
		__in size_t size
		);

	void* MapPhysicalToVirtual(
		__in const PHYSICAL_ADDRESS& address, 
		__in size_t size
		);

protected:
	PHYSICAL_ADDRESS m_addrPhysical;
	size_t m_size;
	void* m_addrVirtual;
};
