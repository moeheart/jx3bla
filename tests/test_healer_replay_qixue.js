/* Run with: node --test tests/test_healer_replay_qixue.js */
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const test = require('node:test');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../static/HealerReplay.js'), 'utf8');
const talentBlock = source.split('//part 4')[1].split('//part 5')[0];

function render(qixue, elements) {
    elements = elements || {
        '#data-4-t': {nodes: [], classes: new Set(['hidden'])},
        '#data-4-h': {nodes: [], classes: new Set()},
    };
    const context = {
        resObj: {qixue},
        document: {
            createTextNode: text => ({type: 'text', text}),
            createElement: tag => {
                assert.equal(tag, 'br');
                return {type: tag};
            },
        },
        $: selector => {
            assert.ok(Object.hasOwn(elements, selector));
            const element = elements[selector];
            const chain = {
                empty() { element.nodes = []; return chain; },
                addClass(name) { element.classes.add(name); return chain; },
                removeClass(name) { element.classes.delete(name); return chain; },
                append(node) {
                    assert.equal(typeof node, 'object', 'Names must be DOM text, never HTML strings');
                    assert.ok(node.type === 'text' || node.type === 'br');
                    element.nodes.push(node);
                    return chain;
                },
            };
            return chain;
        },
    };
    vm.runInNewContext(talentBlock, context, {timeout: 1000});
    return elements;
}

function snapshot(count) {
    return Object.assign({available: 1}, Object.fromEntries(
        Array.from({length: count}, (_, i) => [String(count - i), `奇穴${count - i}`])));
}

function visibleText(elements) {
    return elements['#data-4-t'].nodes.map(node => node.type === 'br' ? '\n' : node.text).join('');
}

for (const count of [9, 4, 10, 12, 6]) {
    test(`renders ${count} recorded slots in order, six per line`, () => {
        const elements = render(snapshot(count));
        const lines = visibleText(elements).split('\n');
        assert.deepEqual(lines.flatMap(line => line.split(',')),
            Array.from({length: count}, (_, i) => `奇穴${i + 1}`));
        assert.ok(lines.every(line => line.split(',').length <= 6));
        assert.equal(elements['#data-4-t'].classes.has('hidden'), false);
        assert.equal(elements['#data-4-h'].classes.has('hidden'), true);
    });
}

test('sparse slots and invalid values do not invent or stringify talents', () => {
    const elements = render({available: 1, '9': '  末项  ', '1': '首项', '2': null,
        '0': '忽略', '01': '忽略', '²': '忽略', note: '说明', '10': {},
        '3': '', '4': '  ', '5': 25, '-1': '忽略'});
    assert.equal(visibleText(elements), '首项,末项');
});

test('unavailable or empty snapshots keep the hint and clear stale names', () => {
    for (const value of [undefined, null, {}, [], {available: 1},
        {available: 0, '1': '部分信息'}, {available: 2, '1': '拒绝'},
        {available: '1', '1': '拒绝'}, {available: 1, '1': '  '}]) {
        const elements = render(value, render(snapshot(9)));
        assert.equal(visibleText(elements), '');
        assert.equal(elements['#data-4-t'].classes.has('hidden'), true);
        assert.equal(elements['#data-4-h'].classes.has('hidden'), false);
    }
});

test('names containing markup are text nodes and boolean availability works', () => {
    const name = '<img src=x onerror=alert(1)> & 测试';
    const elements = render({available: true, '1': name});
    assert.deepEqual(elements['#data-4-t'].nodes, [{type: 'text', text: name}]);
});
