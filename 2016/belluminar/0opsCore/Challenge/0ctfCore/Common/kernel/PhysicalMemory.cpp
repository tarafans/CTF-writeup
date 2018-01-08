#include "drv_common.h"
#include "PhysicalMemory.h"

_IRQL_requires_max_(DISPATCH_LEVEL)
CMmMap::CMmMap( 
	__in ULONG_PTR address,
	__in size_t size
	)
{
	Init(address, size);
}

_IRQL_requires_max_(DISPATCH_LEVEL)
CMmMap::CMmMap( 
	__in const void* address, 
	__in size_t size 
	)
{
	Init((ULONG_PTR)address, size);
}

_IRQL_requires_max_(DISPATCH_LEVEL)
CMmMap::CMmMap( 
	__in const PHYSICAL_ADDRESS& address,
	__in size_t size
	)
{
	Init(static_cast<ULONG_PTR>(address.QuadPart), size);
}

void CMmMap::Init(
	__in ULONG_PTR address,
	__in size_t size
	)
{
	m_size = size;
	RtlZeroMemory(&m_addrPhysical, sizeof(m_addrPhysical));
	m_addrPhysical.QuadPart = address;

	m_addrVirtual = MapPhysicalToVirtual(m_addrPhysical, m_size);
}

_IRQL_requires_max_(DISPATCH_LEVEL)
CMmMap::~CMmMap()
{
	if (m_addrVirtual)//int nt!kipagefault getnexttable IRQL_NOT_LESS_OR_EQUAL
		MmUnmapIoSpace(m_addrVirtual, m_size);
}

void* CMmMap::GetVirtualAddress()
{
	return m_addrVirtual;
}

_IRQL_requires_max_(DISPATCH_LEVEL)
void* CMmMap::MapPhysicalToVirtual(
	__in const PHYSICAL_ADDRESS& address, 
	__in size_t size 
	)
{
	return MmMapIoSpace(address, size, MmNonCached);
}
