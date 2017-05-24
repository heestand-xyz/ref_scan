opTarget = op('TARGET')
blacklist = [op('/sys'), op('/ui'), op('/local')]

# --------------------------------------------- #

import re

totalRefCount = 0
opRegEx = r'op\(\s?[\'\"](.+?)[\'\"]\s?\)'

print(clear())
print('')
print('====== refScan ======')
if opTarget: print(opTarget.path)
print('')

def opScan(parent):
	for child in parent.children:
		if blacklisted(child): continue
		parScan(child)
		scriptScan(child)
		if child.children: opScan(child)

def scriptScan(node):
	global totalRefCount
	if node != me:
		if node.isDAT:
			# ['text', 'table', 'execute', 'chopexec', 'datexec', 'opexec', 'panelexec', 'parexec']
			if re.match(r'text|table|.*exec.*', node.type):
				result = re.finditer(opRegEx, node.text)
				hitCount = 0
				totalCount = 0
				while True:
					try:
						path = next(result).group(1)
						if targetPathCheck(path, node):
							hitCount += 1
						totalCount += 1
						totalRefCount += 1
					except StopIteration:
						break
				if hitCount:
					refs = formatRefs(hitCount, totalCount)
					print('| Txt |', node.path, '|', refs)
			
def parScan(node):
	global totalRefCount
	for par in node.pars():
		if par.isOP:
			selectScan(par, node)
			continue
		if par.isDefault:
			continue
		if par.mode == ParMode.EXPRESSION:
			result = re.finditer(opRegEx, par.expr)
			hitCount = 0
			totalCount = 0
			while True:
				try:
					path = next(result).group(1)
					if targetPathCheck(path, node):
						hitCount += 1
					totalCount += 1
					totalRefCount += 1
				except StopIteration:
					break
			if hitCount:
				refs = formatRefs(hitCount, totalCount)
				print('| Par |', node.path, '|', par.name, '|', par.expr, '|', refs)

def selectScan(par, node):
	opCheck = None
	if par.mode == ParMode.CONSTANT:
		opCheck = par.val
	elif par.mode == ParMode.EXPRESSION:
		opCheck = par.eval()
	if opCheck:
		if opTarget == opCheck:
			print('| Sel |', node.path, '|', par.name, '|')

def formatRefs(hitCount, totalCount):
	refs = ''
	if hitCount == totalCount and totalCount > 1:
		refs = str(hitCount) + ' refs |'
	elif hitCount < totalCount:
		refs = str(hitCount) + '/' + str(totalCount) + ' refs |'
	return refs


def targetPathCheck(path, node):
	# Make Absolute: The path is local and needs to be made global
	opCheckMakeAbsolute = op(node.parent().path + '/' + path)
	opCheckIsAbsolute = op(path)
	if opCheckMakeAbsolute:
		if opTarget == opCheckMakeAbsolute:
			return True
	elif opCheckIsAbsolute:
		if opTarget == opCheckIsAbsolute:
			return True
	return False

def blacklisted(node):
	for black in blacklist:
		if node == black:
			return True
	return False

if opTarget:
	opScan(root)
else:
	print('Error: invalid target op')

print('')
if opTarget: print('total ref count:', totalRefCount)
print('=====================')
print('')