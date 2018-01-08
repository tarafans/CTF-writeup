#pragma once

template<typename ID>
struct CObjComparableById;

template<typename TYPE>
struct CComparableId
{	
	explicit CComparableId(
		__in const TYPE& id
		)
	{
		m_id = id;
	}

	~CComparableId()
	{
		//m_id = 0;
	}
	
	friend
	__forceinline
	bool operator<(
		__in const CComparableId &left, 
		__in const CComparableId &right
		)
	{		
		return (left.m_id < right.m_id);
	}
protected:
	friend struct CObjComparableById<TYPE>;

	TYPE m_id;
};

template<typename ID>
struct CObjComparableById
{
	bool 
	operator()(
		__in const ID& id,
		__in const CComparableId<ID>& obj
		) const
	{
		return (id < obj.m_id);
	}

	bool 
	operator()(
		__in const CComparableId<ID>& obj,
		__in const ID& id
		) const
	{
		return (obj.m_id < id);
	}
};
