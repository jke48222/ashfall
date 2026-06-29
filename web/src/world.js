// ASHFALL — builds the Pompeii vertical-slice courtyard + approach street.
// Every structural piece is tagged with userData.temporal so the W3 toggle can
// morph it Zenith <-> Fall (material swap / visibility).
import * as THREE from 'three';
import { pbr, solid } from './materials.js';

export function buildPompeii(scene) {
  const root = new THREE.Group();
  scene.add(root);
  const temporal = [];     // { mesh, zenithMat, fallMat, zenithVisible, fallVisible }
  const interactables = []; // filled in W4

  const reg = (mesh, opts = {}) => {
    mesh.castShadow = opts.cast !== false;
    mesh.receiveShadow = true;
    root.add(mesh);
    if (opts.temporal) temporal.push({ mesh, ...opts.temporal });
    return mesh;
  };
  const box = (w, h, d) => new THREE.BoxGeometry(w, h, d);
  const cyl = (rt, rb, h, s = 24) => new THREE.CylinderGeometry(rt, rb, h, s);

  // --- materials -----------------------------------------------------------
  const matCobble = pbr('cobblestone', [40, 40]);
  const matAsh = pbr('ash_ground', [40, 40]);
  const matTiles = pbr('floor_tiles', [8, 8]);
  const matPlaster = pbr('plaster_wall', [6, 2]);
  const matBrick = pbr('roman_brick', [6, 2]);
  const matMarble = pbr('marble', [1, 3]);
  const matRoof = pbr('roof_tiles', [4, 4]);
  const matStone = solid(0x8d8378, 0.9);

  // --- ground (cobble -> ash) ---------------------------------------------
  const ground = new THREE.Mesh(new THREE.PlaneGeometry(160, 160), matCobble);
  ground.rotation.x = -Math.PI / 2;
  reg(ground, { cast: false, temporal: { zenithMat: matCobble, fallMat: matAsh } });

  // courtyard mosaic floor
  const floor = new THREE.Mesh(box(16, 0.1, 16), matTiles);
  floor.position.set(0, 0.05, 0);
  reg(floor, { cast: false });

  // --- perimeter walls (plaster -> scorched brick), gap on -X (entrance) ---
  const H = 4.5, T = 0.5, E = 8;
  const wallDefs = [
    [box(16.5, H, T), [0, H / 2, E]],         // +Z
    [box(16.5, H, T), [0, H / 2, -E]],        // -Z
    [box(T, H, 16.5), [E, H / 2, 0]],         // +X
    [box(T, H, 5.5), [-E, H / 2, 5.25]],      // -X north half
    [box(T, H, 5.5), [-E, H / 2, -5.25]],     // -X south half
  ];
  for (const [g, p] of wallDefs) {
    const w = new THREE.Mesh(g, matPlaster);
    w.position.set(...p);
    reg(w, { temporal: { zenithMat: matPlaster, fallMat: matBrick } });
  }

  // --- peristyle columns (standing in Zenith, hidden in Fall) --------------
  const colXs = [-6, -3, 0, 3, 6];
  const colZ = 6.5;
  const placeColumn = (x, z) => {
    const shaft = new THREE.Mesh(cyl(0.38, 0.45, 5, 20), matMarble);
    shaft.position.set(x, 2.6, z);
    reg(shaft, { temporal: { zenithMat: matMarble, fallMat: matMarble, zenithVisible: true, fallVisible: false } });
    const cap = new THREE.Mesh(box(1.1, 0.4, 1.1), matMarble);
    cap.position.set(x, 5.2, z);
    reg(cap, { temporal: { zenithVisible: true, fallVisible: false } });
    // fallen twin (only in Fall) — lying along X
    const fallen = new THREE.Mesh(cyl(0.38, 0.45, 4.2, 20), matMarble);
    fallen.position.set(x + 1.4, 0.45, z);
    fallen.rotation.z = Math.PI / 2;
    fallen.visible = false;
    reg(fallen, { temporal: { zenithVisible: false, fallVisible: true } });
  };
  for (const x of colXs) { placeColumn(x, colZ); placeColumn(x, -colZ); }
  for (const z of [-3, 0, 3]) { placeColumn(6.5, z); placeColumn(-6.5, z); }

  // --- central fountain (primitive, stone) ---------------------------------
  const basin = new THREE.Mesh(cyl(2.1, 2.3, 0.8, 32), matStone);
  basin.position.set(0, 0.4, 0); reg(basin);
  const bowl = new THREE.Mesh(cyl(1.1, 1.3, 0.5, 28), matStone);
  bowl.position.set(0, 1.4, 0); reg(bowl);
  const stem = new THREE.Mesh(cyl(0.25, 0.3, 1.2, 16), matStone);
  stem.position.set(0, 1.0, 0); reg(stem);
  // water surface (zenith only)
  const water = new THREE.Mesh(new THREE.CircleGeometry(2.0, 32),
    new THREE.MeshStandardMaterial({ color: 0x2e6f8e, roughness: 0.08, metalness: 0.0, transparent: true, opacity: 0.85 }));
  water.rotation.x = -Math.PI / 2; water.position.set(0, 0.75, 0);
  reg(water, { cast: false, temporal: { zenithVisible: true, fallVisible: false } });

  // --- statue plinth (hero focal point at +Z end) --------------------------
  const plinth = new THREE.Mesh(box(2, 1.5, 2), matMarble);
  plinth.position.set(0, 0.75, 6.6); reg(plinth);

  // --- rubble piles (Fall only) -------------------------------------------
  for (const [x, z] of [[-5, 6.6], [4.5, -6.8], [6.6, 3], [-6.6, -2.5]]) {
    const r = new THREE.Mesh(box(1.6, 1.0, 1.4), matBrick);
    r.position.set(x, 0.5, z); r.rotation.y = Math.random() * Math.PI;
    r.visible = false;
    reg(r, { temporal: { zenithVisible: false, fallVisible: true } });
  }

  // --- approach street + insula walls (out the -X gap) ---------------------
  const street = new THREE.Mesh(box(40, 0.08, 8), matCobble);
  street.position.set(-28, 0.04, 0); reg(street, { cast: false });
  for (const z of [4.25, -4.25]) {
    const ins = new THREE.Mesh(box(40, 5, 0.5), matPlaster);
    ins.position.set(-28, 2.5, z);
    reg(ins, { temporal: { zenithMat: matPlaster, fallMat: matBrick } });
  }

  // --- Vesuvius backdrop (far silhouette) ----------------------------------
  const vesuvius = new THREE.Mesh(cyl(0, 70, 55, 48),
    new THREE.MeshStandardMaterial({ color: 0x3b352f, roughness: 1.0 }));
  vesuvius.position.set(20, 27, -130);
  reg(vesuvius, { cast: false });

  return { root, temporal, interactables, playerStart: new THREE.Vector3(-44, 1.7, 0), fountain: new THREE.Vector3(0, 1, 0) };
}
