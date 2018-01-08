#include "drv_common.h"
#include "VirtualMemory.h"

_IRQL_requires_max_(DISPATCH_LEVEL)
CVirtMem::CVirtMem(
	__in void* virtualAddress, 
	__in size_t size
	) : m_mem(nullptr),
		m_mdl(nullptr),
		m_lockOperation(IoModifyAccess)
{
	AllocateMdl(virtualAddress, size);
}

CVirtMem::CVirtMem( 
	__in const void* virtualAddress, 
	__in size_t size 
	) : m_mem(nullptr),
		m_mdl(nullptr),
		m_lockOperation(IoReadAccess)
{
	AllocateMdl(const_cast<void*>(virtualAddress), size);
}

_IRQL_requires_max_(DISPATCH_LEVEL)
CVirtMem::~CVirtMem()
{
	if (!m_mdl)
		return;

	if ((m_mdl->MdlFlags & MDL_PAGES_LOCKED))
		MmUnlockPages(m_mdl);

	IoFreeMdl(m_mdl);
}

void 
CVirtMem::AllocateMdl(
	__in void* virtualAddress, 
	__in size_t size
	)
{
	if (ULONG_MAX < size)
		return;

	m_mdl = IoAllocateMdl(virtualAddress, static_cast<ULONG>(size), FALSE, FALSE, nullptr);
}

//Callers of MmProbeAndLockPages must be running at IRQL <= APC_LEVEL for pageable addresses, or at IRQL <= DISPATCH_LEVEL for nonpageable addresses.
_IRQL_requires_max_(APC_LEVEL)
__checkReturn
bool 
CVirtMem::Lock(
	__in bool user
	)
{
	if (!m_mdl)
		return false;

	//already locked ?
	if ((m_mdl->MdlFlags & MDL_PAGES_LOCKED))
		return true;

	__try
	{
		MmProbeAndLockPages(m_mdl, static_cast<KPROCESSOR_MODE>(user ? UserMode : KernelMode), m_lockOperation);
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
		m_mdl->MdlFlags &= ~MDL_PAGES_LOCKED;
	}

	return ((m_mdl->MdlFlags & MDL_PAGES_LOCKED));
}

//Callers of MmUnmapLockedPages must be running at IRQL <= DISPATCH_LEVEL if the pages were mapped to system space. Otherwise, the caller must be running at IRQL <= APC_LEVEL.
_IRQL_requires_max_(APC_LEVEL)
void 
CVirtMem::Unmap()
{
	if (!m_mdl)
		return;

	if ((m_mdl->MdlFlags & MDL_PAGES_LOCKED))
		return;

	if (!m_mem)
		return;

	MmUnmapLockedPages(m_mem, m_mdl);
}

void* 
CVirtMem::Map( 
	__in MEMORY_CACHING_TYPE cacheType,
	__in bool user
	)
{
	if (!m_mdl)
		return nullptr;

	if (m_mem)
		return m_mem;

	if (!Lock(user))
		return nullptr;

	__try
	{
		m_mem = MmMapLockedPagesSpecifyCache(m_mdl, static_cast<KPROCESSOR_MODE>(user ? UserMode : KernelMode), cacheType, NULL, FALSE, NormalPagePriority);
	}
	__except (EXCEPTION_EXECUTE_HANDLER)
	{
		DbgPrint("\nMAP ERROR\n");
	}
	return m_mem;
}

//If AccessMode is UserMode, the caller must be running at IRQL <= APC_LEVEL. If AccessMode is KernelMode, the caller must be running at IRQL <= DISPATCH_LEVEL.
_IRQL_requires_max_(DISPATCH_LEVEL)
__checkReturn
const void* 
CVirtMem::ReadPtr(
	__in_opt MEMORY_CACHING_TYPE cacheType /*= MmCached*/ 
	)
{
	return Map(cacheType, false);
}

_IRQL_requires_max_(DISPATCH_LEVEL)
__checkReturn
void* 
CVirtMem::WritePtr( 
	__in_opt MEMORY_CACHING_TYPE cacheType /*= MmCached */
	)
{
	if (m_lockOperation == IoReadAccess)
		return nullptr;

	return Map(cacheType, false);
}

_IRQL_requires_max_(APC_LEVEL)
const void* 
CVirtMem::ReadPtrUser( 
	__in_opt MEMORY_CACHING_TYPE cacheType /*= MmCached */ 
	)
{
	return Map(cacheType, true);
}

_IRQL_requires_max_(APC_LEVEL)
__checkReturn
void* 
CVirtMem::WritePtrUser( 
	__in_opt MEMORY_CACHING_TYPE cacheType /*= MmCached */ 
	)
{
	if (m_lockOperation == IoReadAccess)
		return nullptr;
		
	return Map(cacheType, true);
}
