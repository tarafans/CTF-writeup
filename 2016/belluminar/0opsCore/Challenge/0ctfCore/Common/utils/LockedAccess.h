#pragma  once

#include "../kernel/Lock.hpp"

template<typename TLOCK, typename TROLOCK, typename TRWLOCK>
class CLockedAccess
{
protected:
	typedef CAutoLock<TLOCK, TROLOCK> read_only_lock;
	typedef CAutoLock<TLOCK, TRWLOCK> read_write_lock;

public:
	/*
	usage : 

	auto lock = <CLockedAccess>.ReadOnlyLockHolder();

	-> now it is locked in scope when variable lock exist!
	*/
	__forceinline
	read_only_lock
	ReadOnlyLockHolder()
	{
		read_only_lock lock(m_lock);
		return lock;
	}

	/*
	usage :

	auto lock = <CLockedAccess>.ReadWriteLockHolder();

	-> now it is locked in scope when variable lock exist!
	*/
	__forceinline
	read_write_lock
	ReadWriteLockHolder()
	{
		read_write_lock lock(m_lock);
		return lock;
	}

protected:
	TLOCK m_lock;
};

using CFastResource = CLockedAccess<CRsrcFastLock, CSharedLockWorker, CExclusiveLockWorker>;
using CSpinResource = CLockedAccess<CSpinLock, CSpinLockWorker, CSpinLockWorker>;

using CExFastResource = CLockedAccess<EX_PUSH_LOCK, CSharedLockWorker, CExclusiveLockWorker>;
using CKSpinResource = CLockedAccess<KSPIN_LOCK, CSpinLockWorker, CSpinLockWorker>;
