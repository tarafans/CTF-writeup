#pragma once

#include "IRQL.hpp"

#include "fltKernel.h"

//-----------------------------------------------------------
// ****************** GENERIC LOCK CLASSES ******************
//-----------------------------------------------------------

/*
#CAutoLock usage : 

	1) CAutoLock<CRsrcFastLock, CSharedLockWorker> auto_lock(typeof(CRsrcFastLock))
	2) CAutoLock<EX_PUSH_LOCK, CSharedLockWorker> auto_lock(&typeof(EX_PUSH_LOCK))
*/

template<typename LOCK, typename WORKER>
class CAutoLock
{
public:
	//LOCK of type CLockHolder
	CAutoLock(
		__inout LOCK& lock
		) : m_lock(lock)
	{
		m_lock.Lock();
	}
	//LOCK of type TLOCK in CLockWorker's & CLockHolder's
	CAutoLock(
		__inout LOCK* lock
		) : m_lock(lock)
	{
		m_lock.Lock();
	}

	~CAutoLock()
	{
		m_lock.Unlock();
	}

	CAutoLock(const CAutoLock&);
private:
	void operator=(const CAutoLock&) = delete;

protected:
	WORKER m_lock;
};

template<typename TLOCK>
class CLockWorker
{
protected:
	explicit CLockWorker(
		__inout TLOCK* lock
		) : m_tLock(lock)
	{
	}

private:
	CLockWorker(const CLockWorker&) = delete;
	void operator=(const CLockWorker&) = delete;

protected:
	TLOCK* m_tLock;
};

template<typename TLOCK>
class CLockHolder
{
protected:
	explicit CLockHolder()
	{
	}

public:
	TLOCK* operator&()
	{
		return &m_tInitLock;
	}

private:
	CLockHolder(const CLockHolder&) = delete;
	void operator=(const CLockHolder&) = delete;

protected:
	TLOCK m_tInitLock;
};


//-----------------------------------------------------------------------
// ****************** FAST MUTEX;IRQL < DISPATCH_LEVEL ******************
//-----------------------------------------------------------------------

class CFastLock : 
	public CLockHolder<FAST_MUTEX>
{
public:
	CFastLock()
	{
		ExInitializeFastMutex(&m_tInitLock);
	}
};

class CFastLockWorker : 
	protected CLockWorker<FAST_MUTEX>
{
public:
	CFastLockWorker(
		__inout CFastLock& lock
		) : CLockWorker(&lock)
	{
	}

	CFastLockWorker(
		__inout FAST_MUTEX* lock
		) : CLockWorker(lock)
	{
	}
	
	_IRQL_requires_max_(APC_LEVEL)
	void Lock()
	{
		ExAcquireFastMutex(m_tLock);
	}

	_IRQL_requires_max_(APC_LEVEL)
	void Unlock()
	{
		ExReleaseFastMutex(m_tLock);
	}
};

//------------------------------------------------------------------------------
// ****************** FAST RESOURCES LOCK; SHARED & EXCLUSIVE ******************
//------------------------------------------------------------------------------

class CRsrcFastLock : 
	public CLockHolder<EX_PUSH_LOCK>
{
public:
	CRsrcFastLock()
	{
		FltInitializePushLock(&m_tInitLock);
	}
};

class CResourceLockWorker  : 
	public CLockWorker<EX_PUSH_LOCK>
{
public:
	CResourceLockWorker(
		__inout EX_PUSH_LOCK* lock
		) : CLockWorker(lock)
	{
	}

	_IRQL_requires_max_(APC_LEVEL)
	void Unlock()
	{
		FltReleasePushLock(m_tLock);
	}
};

class CExclusiveLockWorker : 
	public CResourceLockWorker
{
public:
	CExclusiveLockWorker(
		__inout CRsrcFastLock& lock
		) : CResourceLockWorker(&lock)
	{
	}

	CExclusiveLockWorker(
		__inout EX_PUSH_LOCK* lock
		) : CResourceLockWorker(lock)
	{
	}

	_IRQL_requires_max_(APC_LEVEL)
	void Lock()
	{
		FltAcquirePushLockExclusive(m_tLock);
	}
};

class CSharedLockWorker : 
	public CResourceLockWorker
{
public:
	CSharedLockWorker(
		__inout CRsrcFastLock& lock
		) : CResourceLockWorker(&lock)
	{
	}

	CSharedLockWorker(
		__inout EX_PUSH_LOCK* lock
		) : CResourceLockWorker(lock)
	{
	}

	_IRQL_requires_max_(APC_LEVEL)
	void Lock()
	{
		FltAcquirePushLockShared(m_tLock);
	}
};

//------------------------------------------------
// ****************** SPIN LOCK ******************
//------------------------------------------------

class CSpinLock : 
	public CLockHolder<KSPIN_LOCK>
{
public:
	CSpinLock()
	{
		KeInitializeSpinLock(&m_tInitLock);
	}
};

class CSpinLockWorker : 
	public CLockWorker<KSPIN_LOCK>
{
public:
	CSpinLockWorker(
		__inout CSpinLock& lock
		) : CLockWorker(&lock)
	{
	}

	CSpinLockWorker(
		__inout KSPIN_LOCK* lock
		) : CLockWorker(lock)
	{
	}

	_IRQL_requires_max_(DISPATCH_LEVEL)
	void Lock()
	{
		if (CIRQL::RunsOnDispatchLvl())
			KeAcquireInStackQueuedSpinLockAtDpcLevel(m_tLock, &m_qhandle);
		else
			KeAcquireInStackQueuedSpinLock(m_tLock, &m_qhandle);
	}

	_IRQL_requires_max_(DISPATCH_LEVEL)
	void Unlock()
	{
		if (DISPATCH_LEVEL == m_qhandle.OldIrql)
			KeReleaseInStackQueuedSpinLockFromDpcLevel(&m_qhandle);
		else
			KeReleaseInStackQueuedSpinLock(&m_qhandle);
	}

protected:
	KLOCK_QUEUE_HANDLE m_qhandle;
};
