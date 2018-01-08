#pragma once

#include "drv_common.h"

#include "LockedAccess.h"
#include "../base/ObjDisposer.hpp"
#include "../base/ComparableId.hpp"

#include <boost/intrusive/list.hpp>
#include <boost/intrusive/avltree.hpp>
using namespace boost::intrusive;

template<typename LOCK, typename TREE, typename DISPOSER>
class CLockTree :
	public LOCK,
	public TREE
{
public:
	~CLockTree()
	{
		list<TREE::value_type> defer;

		{//scoped lock
			auto lock = ReadWriteLockHolder();;
			for (auto obj(begin()); obj != end(); obj++)
				defer.push_back(*obj);//safe for deleting outside of lock

			clear();
		}

		defer.clear_and_dispose(DISPOSER());
	}
};

template<typename TREE, typename DISPOSER>
using CFastLockTree = CLockTree<CFastResource, TREE, DISPOSER>;
template<typename TREE, typename DISPOSER>
using CSpinLockTree = CLockTree<CSpinResource, TREE, DISPOSER>;

template<typename TYPE>
using CFastAvl = CFastLockTree< avltree<TYPE>, CObjDisposer<TYPE> >;
template<typename TYPE>
using CSpinAvl = CSpinLockTree< avltree<TYPE>, CObjDisposer<TYPE> >;

template<typename ID>
class CLockedNode :
	public list_base_hook<>,
	public avl_set_base_hook<>,
	public CComparableId<ID>
{
public:
	CLockedNode(
		__in const ID& id
		) : CComparableId(id)
	{}
};
