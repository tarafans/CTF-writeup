#pragma once

#include <ntifs.h>

class CVirtMem
{
public:
	CVirtMem(
		__in void* virtualAddress, 
		__in size_t size
		);

	CVirtMem(
		__in const void* virtualAddress, 
		__in size_t size
		);

	~CVirtMem();

	_IRQL_requires_max_(DISPATCH_LEVEL)
	__checkReturn
	const void* ReadPtr(
		__in_opt MEMORY_CACHING_TYPE cacheType = MmCached
		);

	_IRQL_requires_max_(DISPATCH_LEVEL)
	__checkReturn
	void* WritePtr(
		__in_opt MEMORY_CACHING_TYPE cacheType = MmCached
		);

	_IRQL_requires_max_(APC_LEVEL)
	__checkReturn
	const void* ReadPtrUser(
		__in_opt MEMORY_CACHING_TYPE cacheType = MmCached
		);

	_IRQL_requires_max_(APC_LEVEL)
	__checkReturn
	void* WritePtrUser(
		__in_opt MEMORY_CACHING_TYPE cacheType = MmCached
		);

protected:
	void
	AllocateMdl(
		__in void* virtualAddress,
		__in size_t size
		);

	_IRQL_requires_max_(APC_LEVEL)
	__checkReturn
	bool Lock(
		__in bool user
		);

	void* Map(
		__in_opt MEMORY_CACHING_TYPE cacheType,
		__in bool user
		);

	void Unmap();

protected:
	MDL* m_mdl;
	void* m_mem;
	LOCK_OPERATION m_lockOperation;
};
