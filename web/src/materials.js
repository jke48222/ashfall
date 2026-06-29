// ASHFALL — PBR material library built from the web-optimized PolyHaven kit.
// Each texture set is BaseColor (sRGB) + DirectX normal + ORM-packed `arm`
// (R=AO, G=Roughness, B=Metalness); three reads roughness from .g, metal from .b.
import * as THREE from 'three';

const loader = new THREE.TextureLoader();
const BASE = 'assets/tex/';
const _cache = new Map();

function tex(file, srgb, repeat) {
  const t = loader.load(BASE + file);
  t.wrapS = t.wrapT = THREE.RepeatWrapping;
  t.repeat.set(repeat[0], repeat[1]);
  t.colorSpace = srgb ? THREE.SRGBColorSpace : THREE.NoColorSpace;
  t.anisotropy = 8;
  return t;
}

/** Build (and cache) a tiling PBR material for a kit set. */
export function pbr(name, repeat = [1, 1], opts = {}) {
  const key = `${name}|${repeat[0]}x${repeat[1]}|${JSON.stringify(opts)}`;
  if (_cache.has(key)) return _cache.get(key);
  const map = tex(`${name}_diff.jpg`, true, repeat);
  const normalMap = tex(`${name}_nor.jpg`, false, repeat);
  const arm = tex(`${name}_arm.jpg`, false, repeat);
  const mat = new THREE.MeshStandardMaterial({
    map, normalMap, roughnessMap: arm, metalnessMap: arm,
    metalness: 1.0, roughness: 1.0,
    ...opts,
  });
  _cache.set(key, mat);
  return mat;
}

/** A plain colored PBR material (for accents / greybox bits). */
export function solid(color, roughness = 0.85, metalness = 0.0) {
  return new THREE.MeshStandardMaterial({ color, roughness, metalness });
}
