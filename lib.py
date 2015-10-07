import math, re

tag_regex =         re.compile(r"^[ \t]*(?:(?:INIT:|COND:|REPEAT:)[ \t]*)+", re.IGNORECASE)
init_tag_regex =    re.compile(r"^[ \t]*(?:(?:INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*INIT:", re.IGNORECASE)
cond_tag_regex =    re.compile(r"^[ \t]*(?:(?:INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*COND:", re.IGNORECASE)
repeat_tag_regex =  re.compile(r"^[ \t]*(?:(?:INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*REPEAT:", re.IGNORECASE)
block_tag_regex =   re.compile(r"^[ \t]*(?:(?:INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*BLOCK:[ \t]*(minecraft:)?[a-z_](:\d{1,2})?", re.IGNORECASE)
block_regex =       re.compile(r"^[ \t]*(?:(?:INIT:|COND:|REPEAT:|BLOCK:)[ \t]*)*BLOCK:[ \t]*", re.IGNORECASE)
define_regex =      re.compile(r"^[ \t]*DEFINE:\s*[a-zA-Z0-9_]+", re.IGNORECASE)
define_tag_regex =  re.compile(r"^[ \t]*DEFINE:", re.IGNORECASE)
undefine_regex =    re.compile(r"^[ \t]*UNDEFINE:", re.IGNORECASE)
word_regex =        re.compile(r"[a-zA-Z0-9_]+") # this regex has had me laughing for a while, but i need it
param_regex =       re.compile(r"\((?:[a-zA-Z0-9_]+,)*[a-zA-Z0-9_]+\)")
macro_regex =       re.compile(r"[a-zA-Z0-9_]+\((?:[a-zA-Z0-9_]+,)*[a-zA-Z0-9_]+\)")
import_regex =      re.compile(r"^[ \t]*IMPORT:", re.IGNORECASE)
for_regex =         re.compile(r"^[ \t]*FOR[ \t]*\((?:[a-zA-Z0-9_]+;)?-?\d+(?:\.\d+)?(?:,-?\d+(?:\.\d+)?){0,2}\):[ \t]*$", re.IGNORECASE)
for_tag_regex =     re.compile(r"^[ \t]*FOR", re.IGNORECASE)
endfor_regex =      re.compile(r"^[ \t]*:ENDFOR[ \t]*$", re.IGNORECASE)

comment_regex =     re.compile(r"^[ \t]*#")
skipnewline_regex = re.compile(r"\\[ \t]*$")
line_var_regex =    re.compile(r"\$line\b", re.IGNORECASE)

sin =  lambda string, params, args: repr(math.sin(math.radians(float(args[0]))))
cos =  lambda string, params, args: repr(math.cos(math.radians(float(args[0]))))
tan =  lambda string, params, args: repr(math.tan(math.radians(float(args[0]))))
sinr=  lambda string, params, args: repr(math.sin(float(args[0])))
cosr=  lambda string, params, args: repr(math.cos(float(args[0])))
tanr=  lambda string, params, args: repr(math.tan(float(args[0])))
floor= lambda string, params, args: repr(int(math.floor(float(args[0]))))
ceil=  lambda string, params, args: repr(int(math.ceil(float(args[0]))))
rnd_l= lambda string, params, args: repr(round(float(args[0]), int(args[1])))
add =  lambda string, params, args: repr(float(args[0]) + float(args[1]))
sub =  lambda string, params, args: repr(float(args[0]) - float(args[1]))
mul =  lambda string, params, args: repr(float(args[0]) * float(args[1]))
div =  lambda string, params, args: repr(float(args[0]) / float(args[1]))
pow_l= lambda string, params, args: repr(float(args[0]) **float(args[1]))

lessthan =   lambda a, b: a < b
greatthan =  lambda a, b: a > b
alwaysfalse= lambda *args: False