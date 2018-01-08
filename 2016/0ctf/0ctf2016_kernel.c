#include <linux/module.h>
#include <linux/kernel.h>
#include <linux/miscdevice.h>
#include <linux/init.h>
#include <linux/slab.h>
#include <linux/fs.h>
#include <linux/list.h>
#include <linux/idr.h>
#include <linux/cred.h>
#include <linux/sched.h>
#include <asm/uaccess.h>

struct tasks_t {
	int pid;
	const char *comm;
	const struct cred *cred;
	struct script_t *script;
};

struct script_t {
	size_t size;
	char *content;
};

struct hashtable_t {
	void *table;
	size_t size;
	/* size_t active; */
};

struct cred_t {
	atomic_t usage;
	kuid_t uid;
	kgid_t gid;
	kuid_t suid;
	kgid_t sgid;
	kuid_t euid;
	kgid_t egid;
	kuid_t fsuid;
	kgid_t fsgid;
};

struct qcred_t {
	int pid;
	void __user *buf;
};

struct qcomm_t {
	int pid;
	void __user *buf;
};

struct qscript_t {
	int pid;
	void __user *buf;
};

struct qupdate_script_t {
	int pid;
	size_t size;
	void __user *buf;
};

static struct kmem_cache *task_cachep;

#define LOG(...) printk(KERN_INFO __VA_ARGS__)
#define HT_SIZE 1447
#define MEME_LIST 1337 + 0
#define MEME_REFRESH 1337 + 1
#define MEME_UPDATE 1337 + 2
#define MEME_QCRED 1337 + 3
#define MEME_QCOMM 1337 + 4
#define MEME_QSCRIPT 1337 + 5
#define MEME_UPDATE_SCRIPT 1337 + 6

static int get_hash ( int pid )
{
	return pid % HT_SIZE;	
}

static void *find ( struct hashtable_t *ht, int key )
{
	struct tasks_t **tasks = (struct tasks_t **)(ht->table);
	int index = get_hash(key);
	size_t size = ht->size;
	int i = index;
	void *ret = NULL;

	while ( tasks[i] != NULL )
	{
		if ( tasks[i]->pid == key )
		{
			ret = tasks[i];
			break;
		}

		i = (i + 1) % size;

		if (i == index) 
			break;
	}

	return ret;
}

static int insert ( struct hashtable_t *ht, int key, unsigned long value )
{
	int index = get_hash(key);
	unsigned long *base = (unsigned long *)(ht->table);
	int i = index;	
	size_t size = ht->size;

	while ( base[i] != 0 && (i + 1) % size != index) 
		i = (i + 1) % size;		

	if ( (i + 1) % size == index )
		return -1;

	base[i] = value;

	return 0;
}

static void clean ( struct hashtable_t *ht )
{
	memset(ht->table, 0, ht->size * 0x4);
}

static unsigned long hashtable_ctor ( void )
{
	struct hashtable_t *ht = kmalloc(sizeof(struct hashtable_t), GFP_KERNEL);
	ht->size = HT_SIZE;
	ht->table = kzalloc(ht->size * 0x4, GFP_KERNEL);

	return (unsigned long)ht;
}

static void hashtable_dtor ( struct hashtable_t *ht )
{
	kfree(ht->table);
	kfree(ht);
}

static void ctor ( struct file *file, struct hashtable_t *ht_arg )
{
	struct hashtable_t *ht;
	struct task_struct *iter = current;
	struct tasks_t *item;

	ht = ht_arg ? ht_arg : (struct hashtable_t *)hashtable_ctor();

	do {
		//LOG("%d: %s\n", iter->pid, iter->comm);	
		item = kmem_cache_alloc(task_cachep, GFP_KERNEL);

		if (!item)
			return;

		item->pid = iter->pid;
		item->comm = iter->comm;	
		item->cred = iter->cred;
		item->script = NULL;

		insert(ht, item->pid, (unsigned long)item);

		iter = next_task(iter);
	} while (iter != current);
	
	file->private_data = ht;
}

static int meme_open ( struct inode *inode, struct file *file )
{
	ctor(file, NULL);
	return 0;
}

static int refresh ( struct file *file )
{
	struct hashtable_t *ht = file->private_data;

	if (ht == NULL)
		return -1;

	clean(ht);	
	ctor(file, ht);	
	return 0;
}

static int update ( struct file *file, unsigned long arg )
{
	struct hashtable_t *ht = file->private_data;	
	int pid = arg;

	struct tasks_t *target = find(ht, pid);
	int flag = 0;

	struct task_struct *iter = current;
	
	if (target == NULL)
		goto fail;

	do {

		if (iter->pid == target->pid)
		{
			flag = 1;
			target->comm = iter->comm;
			target->cred = iter->cred;
			break;
		}

		iter = next_task(iter);
	} while (iter != current);

	if (!flag)
		kfree(target);

	return 0;

fail:
	return -1;
}

static int qcred ( struct file *file, unsigned long arg )
{
	struct hashtable_t *ht = file->private_data;
	struct qcred_t argp;

	if (copy_from_user(&argp, (void __user *)arg, sizeof(struct qcred_t)))
		return -1;

	int pid = argp.pid;
	void __user *buf = argp.buf;

	struct tasks_t *target = find(ht, pid);
/*
	printk("pid: %d\n", pid);
	printk("pid: %d\n", target->pid);
	printk("comm: 0x%08x\n", target->comm);
	printk("cred: 0x%08x\n", target->cred);
*/
	int errno = 0;

	if (target == NULL)
		return -1;
	
	if (copy_to_user(buf, target->cred, sizeof(struct cred_t)))
		return errno;

	return 0;
}

static int qcomm ( struct file *file, unsigned long arg )
{
	struct hashtable_t *ht = file->private_data;
	struct qcomm_t argp;

	if (copy_from_user(&argp, (void __user *)arg, sizeof(struct qcomm_t)))
		return -1;

	int pid = argp.pid;
	void __user *buf = argp.buf;

	struct tasks_t *target = find(ht, pid);

	int errno = 0;

	if (target == NULL)
		return -1;
	
	if (copy_to_user(buf, target->comm, 16))
		return errno;

	return 0;
}

static int qscript ( struct file *file, unsigned long arg )
{
	struct hashtable_t *ht = file->private_data;
	struct qscript_t argp;

	if (copy_from_user(&argp, (void __user *)arg, sizeof(struct qscript_t)))
		return -1;

	int pid = argp.pid;
	void __user *buf = argp.buf;

	struct tasks_t *target = find(ht, pid);

/*
	printk("0x%08x\n", target);
	printk("0x%08x\n", target->script);
	printk("0x%08x\n", target->cred);
	printk("0x%08x\n", target->comm);
*/

	int errno = 0;

	if (target == NULL)
		return -1;
	
	if (target->script == NULL)
		return -1;

	if (copy_to_user(buf, &(target->script->size), sizeof(int)))
		return errno;

	if (copy_to_user(buf + sizeof(int), target->script->content, target->script->size))
		return errno;

	return 0;
}

static int qupdate_script ( struct file *file, unsigned long arg )
{
	struct hashtable_t *ht = file->private_data;
	struct qupdate_script_t argp;

	if (copy_from_user(&argp, (void __user *)arg, sizeof(struct qupdate_script_t)))
		return -1;
	
	int pid = argp.pid;
	size_t size = argp.size;
	void __user *buf = argp.buf;

	void *content = NULL;

	struct tasks_t *target = find(ht, pid);
	
	struct script_t *script;

	if (target == NULL)
		return -1;
	
	if (target->script)
	{
		if (size <= target->script->size)
		{
			memset(target->script->content, 0, target->script->size);

			if (copy_from_user(target->script->content, buf, size))
				goto fail;

			target->script->size = size;
		} 
		else
		{
			content = kmalloc(size, GFP_KERNEL);

			if (content == NULL)
				goto fail;

			if (copy_from_user(content, buf, size))
				goto fail;

			kfree(target->script->content);
			target->script->content = content;
			target->script->size = size;
		}
	}
	else
	{
		if (size == 0)
			goto success;

		content = kmalloc(size, GFP_KERNEL);

		if (!content)
			goto fail;

		if (copy_from_user(content, buf, size))
			goto fail;

		if (!target->script)
			script = kmalloc(sizeof(struct script_t), GFP_KERNEL);

		if (!script)
			goto fail;

		script->content = content;
		script->size = size;
		target->script = script;
	}

success:
	return 0;

fail:
	if (content)
		kfree(content);

	return -1;
}

static int list_task ( struct file* file, unsigned long arg )
{
	struct hashtable_t *ht = file->private_data;	
	struct tasks_t **tasks = (struct tasks_t **)(ht->table); 

	unsigned int __user *count = (unsigned int *)arg;
	unsigned int __user *buf = count + 1;

	int i, errno = 0;
	int cnt = 0;
	struct tasks_t *item;
	
	for (i = 0; i < ht->size; i++)
	{
		item = tasks[i];
		if (item)
		{
			if (copy_to_user(buf + cnt, &(item->pid), sizeof(int)))
				return errno;
			cnt++;
		}
	}

	if (copy_to_user(count, &cnt, sizeof(int)))
		return errno;

	return 0;
}

static long meme_ioctl ( struct file *file, unsigned int cmd, unsigned long arg )
{
    long ret = 0;

	switch (cmd)
	{
		case MEME_LIST:
		{
			ret = list_task(file, arg);
			break;
		}

		case MEME_REFRESH:
		{
			ret = refresh(file);
			break;
		}

		case MEME_UPDATE:
		{
			ret = update(file, arg);
			break;
		}

		case MEME_QCRED:
		{
			ret = qcred(file, arg);
			break;
		}

		case MEME_QCOMM:
		{
			ret = qcomm(file, arg);
			break;
		}

		case MEME_QSCRIPT:
		{
			ret = qscript(file, arg);
			break;
		}

		case MEME_UPDATE_SCRIPT:
		{
			ret = qupdate_script(file, arg);
			break;
		}

		default:
		{
			ret = -1;
			break;
		}
	}

    return ret;
}

static int meme_release ( struct inode *inode, struct file *file )
{
	struct hashtable_t *ht = file->private_data;

	if (ht != NULL)
		hashtable_dtor(ht);

    return 0;
}

struct file_operations meme_fops = {
    owner:          THIS_MODULE,
    open:           meme_open,
    release:        meme_release,
    unlocked_ioctl: meme_ioctl,
};

static int __init init_meme ( void )
{
	int ret;
	
//	LOG("%d\n", 2);
//	printk("tasks.next: %x\n", offsetof(struct task_struct, tasks));
//	printk("comm: %x\n", offsetof(struct task_struct, comm));
//	printk("cred: %x\n", offsetof(struct task_struct, cred));
	
	task_cachep = kmem_cache_create("tasks_cache",
									sizeof(struct tasks_t),
									0,
									SLAB_HWCACHE_ALIGN,
									0);

	ret = register_chrdev(1337, "m3m3d4", &meme_fops);

    return 0;
}

static void __exit exit_meme ( void )
{
	kmem_cache_destroy(task_cachep);
	
	unregister_chrdev(1337, "m3m3d4");
}

module_init(init_meme);
module_exit(exit_meme);

MODULE_LICENSE("GPL");

