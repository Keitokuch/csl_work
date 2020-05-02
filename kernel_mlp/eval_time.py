from utils import exec_process

ori_sum = 0
jc_sum = 0
total = 0
dmesg = exec_process(['dmesg'], True)
for line in dmesg.split(b'\n'):
    line = line.decode('utf_8').split(' ')
    if 'cm_time' in line:
        total += 1
        base = line.index('cm_time')
        ori_time, jc_time = line[base+1], line[base+2]
        ori_sum += int(ori_time)
        jc_sum += int(jc_time)

print(f'Original average time: {ori_sum / total : 5f}, JC average time: {jc_sum /total : 5f}')
