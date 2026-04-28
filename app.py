from flask import Flask, render_template, request, jsonify

app = Flask(__name__, template_folder='templates')

# --- Scheduling Algorithms ---
def fcfs(proc):
    procs = sorted(proc, key=lambda x: x['arrival'])
    time = 0
    gantt, results = [], []
    for p in procs:
        if time < p['arrival']: time = p['arrival']
        start = time
        time += p['burst']
        gantt.append({'id': p['id'], 'start': start, 'end': time})
        tat = time - p['arrival']
        results.append({'id': p['id'], 'tat': tat, 'wt': tat - p['burst']})
    return gantt, results

def sjf(proc):
    procs = sorted(proc, key=lambda x: x['arrival'])
    time = 0
    gantt, results = [], []
    ready_queue = []
    while procs or ready_queue:
        while procs and procs[0]['arrival'] <= time: ready_queue.append(procs.pop(0))
        if not ready_queue:
            time = procs[0]['arrival']
            continue
        ready_queue.sort(key=lambda x: x['burst'])
        p = ready_queue.pop(0)
        start = time
        time += p['burst']
        gantt.append({'id': p['id'], 'start': start, 'end': time})
        tat = time - p['arrival']
        results.append({'id': p['id'], 'tat': tat, 'wt': tat - p['burst']})
    return gantt, results

def priority(proc):
    procs = sorted(proc, key=lambda x: x['arrival'])
    time = 0
    gantt, results = [], []
    ready_queue = []
    while procs or ready_queue:
        while procs and procs[0]['arrival'] <= time: ready_queue.append(procs.pop(0))
        if not ready_queue:
            time = procs[0]['arrival']
            continue
        ready_queue.sort(key=lambda x: x['priority'])
        p = ready_queue.pop(0)
        start = time
        time += p['burst']
        gantt.append({'id': p['id'], 'start': start, 'end': time})
        tat = time - p['arrival']
        results.append({'id': p['id'], 'tat': tat, 'wt': tat - p['burst']})
    return gantt, results

def round_robin(proc, quantum):
    procs = sorted(proc, key=lambda x: x['arrival'])
    time = 0
    gantt, results = [], []
    queue = []
    remaining = {p['id']: p['burst'] for p in procs}
    idx = 0
    while idx < len(procs) or queue:
        while idx < len(procs) and procs[idx]['arrival'] <= time:
            queue.append(procs[idx])
            idx += 1
        if not queue:
            time = procs[idx]['arrival']
            continue
        p = queue.pop(0)
        start = time
        exec_time = min(remaining[p['id']], quantum)
        time += exec_time
        remaining[p['id']] -= exec_time
        gantt.append({'id': p['id'], 'start': start, 'end': time})
        while idx < len(procs) and procs[idx]['arrival'] <= time:
            queue.append(procs[idx])
            idx += 1
        if remaining[p['id']] > 0: queue.append(p)
        else:
            tat = time - p['arrival']
            results.append({'id': p['id'], 'tat': tat, 'wt': tat - p['burst']})
    return gantt, sorted(results, key=lambda x: x['id'])

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    data = request.json
    processes = data['processes']
    algo = data['algo']
    quantum = int(data.get('quantum', 2))
    
    if algo == 'FCFS': gantt, res = fcfs(processes)
    elif algo == 'SJF': gantt, res = sjf(processes)
    elif algo == 'Priority': gantt, res = priority(processes)
    elif algo == 'RR': gantt, res = round_robin(processes, quantum)
    else: return jsonify({'error': 'Algorithm not found'})
    return jsonify({'gantt': gantt, 'results': res})

if __name__ == '__main__':
    app.run(debug=True)