import os
import sys
import subprocess

TEST_COUNT=0

def runtest(name, eval, expect, filename="statistics.json"):
  global TEST_COUNT
  TEST_COUNT += 1
  
  print(str(TEST_COUNT) + ". " + name)
  dir = os.path.dirname(os.path.realpath(__file__))
  retval = subprocess.call(["python", dir+"/../jm_eval_json.py", "--if="+dir+"/"+filename, '--eval='+eval])
  
  if retval == expect:
    print("\tPASS")
    return 0
  else:
    print("\tFAIL")
    return 1

if __name__ == '__main__':
  retval = 0
  
  tests = [
    ["Single Condition (valid)", "Total.errorPct<5", 0],
    ["Two Conditions (valid)", "Total.errorPct<5;Total.pct2ResTime<1000", 0],
    ["Two Conditions (one fails)", "Total.errorPct<5;Total.errorPct>5", 1],
    ["Condition Evals to False (valid)", "Total.errorPct==100", 1],
    ["Invalid Operator", "Total.errorPct<>5", 1],
    ["Invalid JSON Prop", "Invalid.Prop<5", 1],
    ["Invalid JSON Syntax", "3Invalid..Sytax<5", 1],
    ["RHS not a number", "Total.errorPct<five", 1],
    ["RHS missing", "Total.errorPct<", 1],
    ["LHS missing", "<5", 1],
    ["Operator missing", "Total.errorPct5", 1],
    ["Nonexistent input file", "Total.errorPct<5", 1, "foo.json"],
    ["Syntactically invalid input file", "Total.errorPct<5", 1, "invalid.json"]
  ]
  
  for test in tests:
    if len(test) > 3:
      retval += runtest(test[0], test[1], test[2], test[3])
    else:
      retval += runtest(test[0], test[1], test[2])
  
  print("\n----------------------------------------------")
  print("Tests run (" + str(TEST_COUNT) + "), Passed (" + str(TEST_COUNT-retval) + "), Failed (" + str(retval) + ")")
  
  if retval == 0:
    print("All Tests Passed.")
  else:
    print(str(retval) + " tests failed. See output for details.")
  
  sys.exit(retval)