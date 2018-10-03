#!/usr/bin/env python

# This is a personally developed stuff that I (Alex Yamauchi) created, circa
# 2014, prior to my employment at Hotschedules.  I am adding it here since I
# use it constantly and think others may find it useful.  I plan to publish
# this, along with some other shell utility content, at some point -- under
# and unopensource license and reserve all rights to do so.

# Not really needed except for debugging.
import sys
import os

from copy import deepcopy
import simplejson as json

def debug(tag,message):
    if 'DEBUG' in os.environ:
        if type(message).__name__ in ('list','dict'):
            message = json_formatted(message)
        sys.stderr.write('DEBUG tag=%s:\n%s\n' %(tag,message))

def json_formatted(*args,**kwargs):
    kwargs.update({ 'indent': 2, 'sort_keys': True })
    return json.dumps(*args,**kwargs)

def reformat_data_diff(data):
    # The format used data_diff lends itself to recursion, but it's
    # difficult to work with in the Nagios database processing.

    if not type(data).__name__ == 'dict':
        return [ data, data ]

    ret_val = [ {}, {} ]

    for k in data:
        if type(data[k]).__name__ == 'list':
            [ ret_val[0][k], ret_val[1][k] ] = data[k]
        else:
            [ ret_val[0][k], ret_val[1][k] ] = reformat_data_diff(data[k])

    return ret_val

def data_diff(a,b,list_as_set=True,by_ref=True):

    # Provide a diff of two nested datastructures (hierarchal dicts).
    # The base data structure needs to a dict, since the existence of
    # unique keys is crucial for the simple comparison logic used here.
    # Non-primitive types in the hierarchy should be avoided.  Note
    # that this function is recursive and can be quite a resource pig
    # with large data structures.

    # The option "list_as_set" and address how to treat lists in the
    # hierarchy, since there are no unique keys available.  The "by_ref"
    # argument determines whether mutable objects in the output are
    # referenced or deepcopied.

    if not type(a).__name__  == type(b).__name__:
        raise Exception('Base data type mismatch.')

    if type(a).__name__ == 'dict':
        ret_val = {}
    elif type(a).__name__ == 'list':
        ret_val = []
    else:
        raise Exception('Input type must be "list" or "dict".')

    if type(ret_val).__name__ == 'dict':

        if by_ref:
            copy = lambda x: x
        else:
            copy = lambda x: deepcopy(x)

        for key in set(a.keys()) - set(b.keys()):
            ret_val[key] = [ copy(a[key]), None ]

        for key in set(b.keys()) - set(a.keys()):
            ret_val[key] = [ None, copy(b[key]) ]

        for key in set(a.keys()) & set(b.keys()):

            if type(a[key]).__name__ == type(b[key]).__name__:
                if type(a[key]).__name__ in ('list','dict'):
                    ret_val[key] = data_diff(a[key],b[key],list_as_set=list_as_set,by_ref=by_ref)

                    if len(ret_val[key]) == 0:
                        del ret_val[key]

                else:
                    try:
                        # This is really designed for primitive data types,
                        # but allow for others if comparators are defined.
                        cmp = a[key] == b[key]
                    except:
                        raise Exception('Type "%s" has no comparator.' %(type(a[key])))
                    else:
                        if not cmp:
                            ret_val[key] = [ copy(a[key]) , copy(b[key]) ]
            else:
                ret_val[key] = [ copy(a[key]), copy(b[key]) ]

    else:

        # All this to try to get some keys.  Really, really ugly if we ever
        # get a list of deeply nested data structures.

        # Make some content accessible hashes (JSON).  This automatically
        # eliminates duplicates.

        ca = {
            'a': dict([ (json.dumps(elem,sort_keys=True),elem) for elem in a ]),
            'b': dict([ (json.dumps(elem,sort_keys=True),elem) for elem in b ])
        }

        if by_ref:
            copy = lambda k,v: v
        else:
            copy = lambda k,v: json.loads(k)

        ret_val.append([ copy(k,ca['a'][k]) for k in ca['a'] if not k in ca['b'] ])
        ret_val.append([ copy(k,ca['b'][k]) for k in ca['b'] if not k in ca['a'] ])

        if reduce(lambda a,b: len(a)+len(b), ret_val) == 0:
            ret_val = []

    return ret_val

def data_encode(data,enc_type=unicode):

    # Just dumb.  This JSON library is not consistently encode data on
    # loads -- it alternates between 'str' and 'unicode' types with no
    # discernable regularity -- which wreaks havoc with type comparisons.

    if enc_type.__name__ == 'unicode':
        other_type = str
    else:
        other_type = unicode

    if type(data).__name__ == 'dict':
        for key in data.keys():
            enc_key = enc_type(key)
            if type(key).__name__ == other_type.__name__:
                tmp = data[key]
                del data[key]
                data[enc_key] = tmp
            if type(data[enc_key]).__name__ in ('list','dict'):
                data_encode(data[enc_key])
            elif type(data[enc_key]).__name__ == other_type.__name__:
                data[enc_key] = enc_type(data[enc_key])
    elif type(data).__name__ == 'list':
        for elem in data:
            if type(elem).__name__ in ('list','dict'):
                data_encode(elem)
            elif type(elem).__name__ == other_type.__name__:
                elem = enc_type(elem)

    return data

def quotemeta(str,**kwargs):
    # This is needed all over the place and painful when type checks
    # must also be performed.
    if 'type' in kwargs:
        type = kwargs['type']
    else:
        type = 'mysql'

    if 'replace' in dir(str) and type in ('mysql'):
        return str.replace('\\','\\\\').replace("'","\\'")
    else:
        return str

def count_if(*args,**kwargs):

    if 'comp' in kwargs:
        cond = kwargs['comp']
    else:
        cond = lambda a: a

    return len([ x for x in args if cond(x) ])

def xor(*args,**kwargs):
    # Really surpised that this is not a built-in.
    return count_if(*args,**kwargs) == 1

def iff(*args,**kwargs):
    # Go ahead and add the other common logical function.
    # Returns True only if all args are either True or False.
    return count_if(*args,**kwargs) in (0,len(args))

def none_or_null(*args,**kwargs):
    # This tends to be a really annoying bit of code and constantly
    # needed since an exception is thrown if the len() function is
    # applied to None type.  If the two types are considered equivalent,
    # then this function eliminates the need for a two-stage evaluation.

    ret_val = []

    for a in args:
        if a == None:
            ret_val.append(True)
        else:
            # Raise the exception if the data has no __len__ attribute.
            ret_val.append(len(a) == 0)

    if len(ret_val) > 1:
        return ret_val
    else:
        # If passed a non-list argument, return the first value instead
        # of a singleton list.
        return ret_val[0]

if __name__ == '__main__':

    a = { 'a': [ 0,1,2,3,4 ], 'b': { 1: 'this', 2: 'that' } }
    b = { 'a': [ 1,3,4,5,6 ], 'b': { 1: 'this', 2: 'there', 3: 'other thing' }, 'c': { 1: { 2:3 } } }

    #diff = data_diff(a,b)

    # This is the structure for most of the Nagios cache data.
    c = { 'object_type': { 'object_key': { 'field_name1': 'field_value1', 'field_name2': 'field_value2' }}}
    d = { 'other_object_type': { 'object_key': { 'field_name1': 'other_field_value1', 'field_name2': 'other_field_value2' }}}

    diff = data_diff(c,d)

    print json.dumps(a,sort_keys=True,indent=2)
    print json.dumps(b,sort_keys=True,indent=2)
    print json.dumps(diff,sort_keys=True,indent=2)

    print json.dumps(reformat_data_diff(diff),sort_keys=True, indent=2)

    #e = [ 1,2,3,4 ]
    #f = [ 3,4,5,6 ]
    #print json.dumps(data_diff(e,f),sort_keys=True,indent=2)

    print xor(True,False,False)
    print xor(True,True,False)

    print iff(False,False,False)
    print iff(True,True,True)
    print iff(True,False,True)

    print count_if(None, 'missing', 'null', None, 'missing','missing', comp=lambda a: a == None)
    print count_if(None, 'missing', 'null', None, 'missing','missing', comp=lambda a: a == 'missing')
    print count_if(None, 'missing', 'null', None, 'missing','missing', comp=lambda a: a == 'null')
    print count_if(None, 'missing', 'null', None, 'missing','missing', comp=lambda a: a == 'not here')
