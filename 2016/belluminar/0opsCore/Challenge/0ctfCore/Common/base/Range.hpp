#pragma once

template<class TYPE>
struct CRange
{
	//implicit
	CRange(
		__in const TYPE* begin, 
		__in const TYPE* end = nullptr
		) : m_begin(reinterpret_cast<size_t>(begin)), 
			m_end(reinterpret_cast<size_t>(end ? end : begin)) 
	{
	};

	CRange(
		__in size_t begin = 0, 
		__in size_t end = 0
		) : m_begin(begin), 
			m_end(end ? end : begin)
	{
	};

public:
	void 
	Reset(
		__in const TYPE* begin
		)
	{
		Set(begin, begin);
	};
	void 
	Set(
		__in TYPE* begin,
		__in TYPE* end
		)
	{
		Begin() = begin;
		End() = end;
	};

	bool 
	IsInRange(
		__in const TYPE* address
		) const
	{
		return IsInRange(reinterpret_cast<size_t>(address));
	};

	bool 
	IsInRange(
		__in size_t address
		) const
	{
		return (m_end >= address && address >= m_begin);
	};

	void 
	SetSize(
		__in size_t size
		)
	{ 
		m_end = max(m_begin + size - 1, m_end); 
	};

	size_t 
	GetSize()
	{ 
		return (m_end - m_begin + 1); 
	};

	TYPE*&
	Begin() const
	{
		return (TYPE*&)(m_begin);
	};

	TYPE*& 
	End() const
	{
		return (TYPE*&)(m_end);
	};
	
	size_t&
	SBegin()
	{
		return m_begin;
	};

	size_t&
	SEnd()
	{
		return m_end;
	};
	/*
	TYPE&
	operator[](
		__in size_t index
		)
	{
		return Begin()[index];
	}
	*/
protected:
	static 
	inline 
	bool 
	IsOverlaping(
		__in const CRange &left, 
		__in const CRange &right
		)
	{
		return !(left.Begin() > right.End() || right.Begin() > left.End());
	}

	friend
	bool 
	operator>(
		__in const CRange &left, 
		__in const CRange &right
		)
	{
		if (IsOverlaping(left, right))
			return false;

		return (left.m_begin > right.m_begin);
	}

	friend
	bool 
	operator<(
		__in const CRange &left, 
		__in const CRange &right
		)
	{
		return (right > left);
	}

	friend
	bool 
	operator==(
		__in const CRange &left, 
		__in const CRange &right
		)
	{
		return IsOverlaping(left, right);
	}

private:
	size_t m_begin;
	size_t m_end;
};
