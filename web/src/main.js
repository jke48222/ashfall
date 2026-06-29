// ASHFALL — web build. Renderer, HDRI lighting, world, time-toggle, FX, audio.
import * as THREE from 'three';
import { OrbitControls } from 'three/addons/controls/OrbitControls.js';
import { RGBELoader } from 'three/addons/loaders/RGBELoader.js';
import { buildPompeii } from './world.js';
import { Ashfall } from './fx.js';
import { AudioManager } from './audio.js';
import { Temporal } from './temporal.js';

const canvas = document.getElementById('scene');
const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, powerPreference: 'high-performance' });
renderer.setPixelRatio(Math.min(devicePixelRatio, 2));
renderer.setSize(innerWidth, innerHeight);
renderer.shadowMap.enabled = true;
renderer.shadowMap.type = THREE.PCFSoftShadowMap;
renderer.toneMapping = THREE.ACESFilmicToneMapping;
renderer.toneMappingExposure = 1.05;

const scene = new THREE.Scene();
scene.fog = new THREE.Fog(0xc9d6e6, 90, 320);

const camera = new THREE.PerspectiveCamera(60, innerWidth / innerHeight, 0.1, 2000);
camera.position.set(-10, 6, 12);

const controls = new OrbitControls(camera, canvas);
controls.target.set(0, 2.5, 0);
controls.enableDamping = true;
controls.maxPolarAngle = Math.PI * 0.495;
controls.minDistance = 3; controls.maxDistance = 80;

const sun = new THREE.DirectionalLight(0xfff0d8, 3.2);
sun.position.set(40, 55, 25);
sun.castShadow = true;
sun.shadow.mapSize.set(2048, 2048);
sun.shadow.camera.near = 1; sun.shadow.camera.far = 220;
Object.assign(sun.shadow.camera, { left: -50, right: 50, top: 50, bottom: -50 });
sun.shadow.bias = -0.0003;
scene.add(sun);
const hemi = new THREE.HemisphereLight(0xbfd4ff, 0x6b5a44, 0.28);
scene.add(hemi);

const game = buildPompeii(scene);
const fx = new Ashfall(scene);
const audio = new AudioManager();

const pmrem = new THREE.PMREMGenerator(renderer);
pmrem.compileEquirectangularShader();
const rgbe = new RGBELoader();
let temporal = null;

rgbe.load('assets/hdri/zenith_sky.hdr', (hdr) => {
  hdr.mapping = THREE.EquirectangularReflectionMapping;
  const env = pmrem.fromEquirectangular(hdr).texture;
  scene.environment = env;
  scene.background = hdr;
  temporal = new Temporal({
    scene, game, sun, hemi, renderer, fx, audio,
    envZenith: env, envFall: env, bgZenith: hdr, bgFall: new THREE.Color(0x2a1208),
  });
  document.getElementById('loading')?.remove();
});
rgbe.load('assets/hdri/fall_sky.hdr', (hdr) => {
  hdr.mapping = THREE.EquirectangularReflectionMapping;
  const env = pmrem.fromEquirectangular(hdr).texture;
  if (temporal) temporal.envFall = env;
});

// --- toggle input ----------------------------------------------------------
function doToggle() {
  if (!temporal) return;
  audio.start();
  temporal.toggle();
  setHud();
}
addEventListener('keydown', (e) => {
  if (e.code === 'KeyQ' || e.code === 'KeyT' || e.code === 'Space') { e.preventDefault(); doToggle(); }
});
window.__ashfall = { toggle: () => { if (temporal) { temporal.toggle(); setHud(); } }, state: () => temporal && temporal.state };
canvas.addEventListener('pointerdown', () => { if (!audio.started) audio.start(); });

addEventListener('resize', () => {
  camera.aspect = innerWidth / innerHeight;
  camera.updateProjectionMatrix();
  renderer.setSize(innerWidth, innerHeight);
});

const clock = new THREE.Clock();
function tick() {
  const dt = Math.min(clock.getDelta(), 0.05);
  controls.update();
  if (temporal) temporal.update(dt);
  fx.update(dt, camera.position);
  audio.update(dt);
  renderer.render(scene, camera);
  requestAnimationFrame(tick);
}
tick();

// --- HUD -------------------------------------------------------------------
const ui = document.getElementById('ui');
function setHud() {
  const st = temporal ? temporal.state : 'ZENITH';
  const era = st === 'FALL' ? 'THE FALL · 79 AD' : 'THE ZENITH · golden noon';
  ui.innerHTML = `
    <div style="position:absolute;left:32px;top:26px">
      <div style="font-size:32px;letter-spacing:3px">ASHFALL</div>
      <div style="font-size:12px;opacity:.7;letter-spacing:2px">THE LAST HOURS OF POMPEII</div>
    </div>
    <div style="position:absolute;left:50%;top:24px;transform:translateX(-50%);text-align:center">
      <div style="font-size:15px;letter-spacing:4px;opacity:.85">${era}</div>
    </div>
    <button id="toggleBtn" style="pointer-events:auto;position:absolute;left:50%;bottom:28px;transform:translateX(-50%);
      background:rgba(20,12,8,.55);color:#f3e9d6;border:1px solid rgba(243,233,214,.35);
      padding:12px 22px;border-radius:30px;font-family:inherit;font-size:14px;letter-spacing:2px;cursor:pointer;backdrop-filter:blur(4px)">
      ⟲ SHIFT TIME &nbsp;·&nbsp; [Q] / tap</button>
    <div id="loading" style="position:absolute;right:24px;bottom:20px;font-size:12px;opacity:.6">loading…</div>`;
  document.getElementById('toggleBtn').onclick = doToggle;
  if (!temporal) document.getElementById('loading').textContent = 'loading…';
}
setHud();
