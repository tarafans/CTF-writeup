#pragma once

template<typename TYPE, typename ID>
class CRuntimeBoostedComparator
{
public:
	virtual
	__checkReturn
	bool
	Cmp(
		__in const TYPE&,
		__in const ID&
		) const
	{
		return false;
	}

	virtual
	__checkReturn
	bool
	Cmp(
		__in const ID&,
		__in const TYPE&
		) const
	{
		return false;
	}
};
