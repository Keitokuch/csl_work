from utils import exec_process

total = 0
correct = 0
dmesg = exec_process(['dmesg'], True)
for line in dmesg.split(b'\n'):
    line = line.decode('utf_8').split(' ')
    if 'can_migrate' in line:
        total += 1
        base = line.index('can_migrate')
        ori_cm, jc_cm = line[base+1], line[base+2]
        if ori_cm == jc_cm:
            correct += 1
        else:
            print(line)

print(f'{correct} correct decisions in {total} triggers')
