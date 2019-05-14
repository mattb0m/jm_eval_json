##########################################################################################################################
# FILE: jm_eval_json.py
# AUTH: Matthew Baum
# DATE: 2018/05/01
# DESC: Todo...
# PRMS:
#     --if:   The input file to process (required: TRUE)
#     --eval: Semicolon-delimited list of conditions to evaluate on the target JSON file (required: TRUE)
# NOTE: Example:
#   python jm_eval_json.py --if=test/statistics.json --eval="Total.errorPct<5;Total.pct2ResTime<1000" --verbose
##########################################################################################################################
import sys
import json
import re
import numbers

# Script globals
g_SCRIPT_VERSION = '1.0'
g_arg_fin = ''
g_arg_eval = ''
g_arg_verbose = False
g_EXIT_PASS = 0
g_EXIT_FAIL = 1

#--------------------------------------------------------------------------
# Helpers: prettily print exceptions and print if VERBOSE flag
#--------------------------------------------------------------------------
def printerr(pre, err):
  print("ERROR:", pre, "(", err.errno, "):\n    ->", err.strerror)

def printifv(str):
  global g_arg_verbose
  if g_arg_verbose:
    print(str)

#--------------------------------------------------------------------------
# Print formatted program help message
#--------------------------------------------------------------------------
def print_help():
  global g_SCRIPT_VERSION
  
  msg = """  CSV Stats Cruncher (v{0}):
    This script is meant as a post-processing step for Jmeter 5.1.1+ load tests
    which optionally generate summary stats in JSON format pon test completion.
    
  Command line arguments:
    NOTE: All arguments with values must be supplied in the form: --key=value
    
    --if:     The input file to process (required: TRUE)
    --eval
    --verbose
    --help
  """
  
  print(msg.format(g_SCRIPT_VERSION))

#--------------------------------------------------------------------------
# Parse command line arguments to this script (of the form "--key=value")
#--------------------------------------------------------------------------
def parse_args(argv):
  global g_arg_fin, g_arg_eval, g_EXIT_PASS, g_arg_verbose
  
  for arg in argv:
    if arg[0] == '-' and arg[1] == '-':
      if arg[2:] == "help":
        print_help()
        sys.exit(g_EXIT_PASS)
      
      if arg[2:] == "verbose":
        g_arg_verbose = True
      
      pair = arg[2:].split('=', 1)
      if len(pair) == 2:
        if pair[0] == 'if':
          g_arg_fin = pair[1]
        elif pair[0] == 'eval':
          g_arg_eval = pair[1]

#--------------------------------------------------------------------------
# Read JSON file and deserialize into object
#--------------------------------------------------------------------------
def json_file_to_obj(path):
  f = open(path, 'rb')
  json_str = f.read()
  f.close()
  obj = json.loads(json_str)
  return obj

def eval_comparison(lhs, rhs, cmp):
  if cmp == '<':
    return lhs<rhs
  elif cmp == '>':
    return lhs>rhs
  elif cmp == '<=':
    return lhs<=rhs
  elif cmp == '>=':
    return lhs>=rhs
  elif cmp == '==':
    return lhs==rhs
  elif cmp == '!=':
    return lhs!=rhs
  else:
    printifv("Error: Invalid operator: " + cmp)
    return False
  
def eval_expr(obj, expr):
  retval = True
  expr_regex = "([a-zA-Z][\\w\\.]*)([<>=!]+)([\\d\\.]+)"
  
  printifv("Evaluating expression: '" + expr + "'")
  
  matches = re.match(expr_regex, expr)
  if matches is None:
    printifv(".... Invalid expression!")
    return False
  
  lhs = matches.group(1)
  cmp = matches.group(2)
  rhs = matches.group(3)
  #print(lhs+"|"+cmp+"|"+rhs)
  
  fields = lhs.split('.')
  attr = obj

  for field in fields:
    attr = attr[field]
  
  if not isinstance(attr, numbers.Number):
    printifv(".... Field must be a number!")
    return False
  
  try:
    rhs = float(rhs)
  except:
    printifv(".... RHS must be a number!")
    return False
  
  retval = eval_comparison(attr, rhs, cmp)
  
  if retval:
    printifv("....(PASS)")
  else:
    printifv("....(FAIL)")
  
  return retval

def eval_all(obj, expr_list_str):
  retval = True
  expr_list = expr_list_str.split(';')
  
  for expr in expr_list:
    retval = retval and eval_expr(obj, expr)
  
  return retval

#--------------------------------------------------------------------------
# Script entry point
#--------------------------------------------------------------------------
if __name__ == '__main__':
  retval = g_EXIT_PASS
  
  print('\n')
  parse_args(sys.argv)
  
  if g_arg_fin == '' or g_arg_eval == '':
    print("ERROR: args 'if' and 'eval' must be specified")
    sys.exit(g_EXIT_FAIL)
  else:
    printifv("INFO: evaluating stats file '" + g_arg_fin + "' ...")
    obj = json_file_to_obj(g_arg_fin)
    retval = eval_all(obj, g_arg_eval)
  
  sys.exit(g_EXIT_PASS if retval else g_EXIT_FAIL)