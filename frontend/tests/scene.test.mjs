import test from 'node:test';
import assert from 'node:assert/strict';
import {scaleScene} from '../features/editor/lib/scene.ts';
const items=[{id:1,object:'book',x:10,y:20,rotation:0,role:'main'},{id:2,object:'phone',x:110,y:80,rotation:35,role:'background'}];
const dimensions=()=>[100,50];
test('shared scaling preserves relative distances, rotation, roles and source scene',()=>{
 const original=structuredClone(items);const result=scaleScene(items,dimensions,1.5);
 assert.equal(result[1].x-result[0].x,(items[1].x-items[0].x)*1.5);
 assert.equal(result[1].y-result[0].y,(items[1].y-items[0].y)*1.5);
 assert.equal(result[1].rotation,35);assert.equal(result[1].role,'background');assert.deepEqual(items,original);
});
test('identity scale leaves scene intact',()=>assert.deepEqual(scaleScene(items,dimensions,1),items));
test('empty scene can be scaled',()=>assert.deepEqual(scaleScene([],dimensions,1.5),[]));
