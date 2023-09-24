from pprint import pprint

def doTabs(tabs):
	# Print number of tabs
	for _ in range(tabs):
		print("\t", end="")

def pv(obj):
	# Print variables of an object cleanly
	pprint(vars(obj))

def pt(tabs, *objs):
	# Print objects without separation
	doTabs(tabs)
	limit = len(objs)
	for i, obj in enumerate(objs):
		if i == limit - 1:
			print(obj)
		else:
			print(obj, end="  ;  ")

def pa(objs, tabs):
	# Print each item in an iterable
	doTabs(tabs)
	for obj in objs:
		pp(obj, tabs+1)

def ps(obj):
	# Print the object simply
	if len(str(obj)) < 21:
		print(obj)
	else:
		try:
			size = f", with size {len(obj)}"
		except AttributeError:
			size = ""
		print(f"{type(obj)} object{size}")

def pp(obj, tabs = 0):
	# Smart print for each item
	match type(obj):
		case list():
			pa(obj, tabs)
		case tuple():
			pa(obj, tabs)
		case dict():
			for k, v in obj.items():
				pt(tabs, k, v)
		case other:
			print(obj)
