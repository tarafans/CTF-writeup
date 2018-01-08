#pragma once

#include <ntifs.h>

class CIRQL
{
#define BAD_IRQL 0xFF

protected:
	explicit CIRQL(
		KIRQL irqlLevel
		)
	{
		if (NT_VERIFY(KeGetCurrentIrql() <= irqlLevel))
			KeRaiseIrql(irqlLevel, &m_oldIRQL);
		else
			m_oldIRQL = BAD_IRQL;
	}
public:
	~CIRQL()
	{
		if (m_oldIRQL != BAD_IRQL)
			KeLowerIrql(m_oldIRQL);
	}

	__checkReturn
	bool IsIrqlRaised()
	{
		return (m_oldIRQL != BAD_IRQL);
	}

	static
	__checkReturn
	bool SufficienIrql(
		__in KIRQL irql
		)
	{
		return (irql >= KeGetCurrentIrql());
	}

	static
	__checkReturn
	bool RunsOnPassiveLvl()
	{
		return (PASSIVE_LEVEL == KeGetCurrentIrql());
	}

	static
	__checkReturn
	bool RunsOnApcLvl()
	{
		return (APC_LEVEL == KeGetCurrentIrql());
	}

	static
	__checkReturn
	bool RunsOnDispatchLvl()
	{
		return (DISPATCH_LEVEL == KeGetCurrentIrql());
	}

protected:
	KIRQL m_oldIRQL;
};

class CDispatchLvl : public CIRQL
{
public:
	CDispatchLvl() : CIRQL(DISPATCH_LEVEL)
	{
	}
};

class CApcLvl : public CIRQL
{
public:
	CApcLvl() : CIRQL(APC_LEVEL)
	{
	}
};
