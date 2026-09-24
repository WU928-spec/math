import math, random, itertools
import numpy as np
c=(1+math.sqrt(37))/6; LOW=1.5*(c-1)
exec(open('/tmp/m3_sim2.py').read().split("random.seed")[0].split("OPTS=")[0])
OPTS={9:make_opt(9)}
random.seed(3); worst=-9
for _ in range(3000):
    p=sorted([random.random()**random.choice([1,2,3]) for _ in range(9)], reverse=True)
    p=sorted([max(x,LOW+1e-9) for x in p], reverse=True)
    r,asg,load=A3(p)
    d=r-(p[0]+p[3]+p[8])
    if d>worst: worst=d; rec=(p[:],r,p[0]+p[3]+p[8],asg,load)
print("n=9: max( C_A3 - (p1+p4+p9) ) = %.5f"%worst)
print("  witness p=%s"%(["%.4f"%x for x in rec[0]]))
print("  C_A3=%.4f  p1+p4+p9=%.4f  asg=%s loads=%s"%(rec[1],rec[2],rec[3],["%.4f"%x for x in rec[4]]))
