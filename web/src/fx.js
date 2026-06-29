// ASHFALL — falling-ash + ember particle systems (shown only in the Fall state).
import * as THREE from 'three';

export class Ashfall {
  constructor(scene, { count = 6000, area = 120, height = 60 } = {}) {
    this.area = area; this.height = height;
    const pos = new Float32Array(count * 3);
    this.vel = new Float32Array(count);
    for (let i = 0; i < count; i++) {
      pos[i * 3] = (Math.random() - 0.5) * area;
      pos[i * 3 + 1] = Math.random() * height;
      pos[i * 3 + 2] = (Math.random() - 0.5) * area;
      this.vel[i] = 2 + Math.random() * 4;
    }
    const geo = new THREE.BufferGeometry();
    geo.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    const mat = new THREE.PointsMaterial({
      color: 0xb9b2a8, size: 0.12, transparent: true, opacity: 0.0,
      depthWrite: false, sizeAttenuation: true,
    });
    this.points = new THREE.Points(geo, mat);
    this.points.frustumCulled = false;
    scene.add(this.points);

    // embers — sparse, glowing orange, additive
    const ec = 400;
    const ep = new Float32Array(ec * 3);
    this.evel = new Float32Array(ec);
    for (let i = 0; i < ec; i++) {
      ep[i * 3] = (Math.random() - 0.5) * area;
      ep[i * 3 + 1] = Math.random() * height;
      ep[i * 3 + 2] = (Math.random() - 0.5) * area;
      this.evel[i] = 1 + Math.random() * 2;
    }
    const egeo = new THREE.BufferGeometry();
    egeo.setAttribute('position', new THREE.BufferAttribute(ep, 3));
    this.embers = new THREE.Points(egeo, new THREE.PointsMaterial({
      color: 0xff7a1e, size: 0.18, transparent: true, opacity: 0.0,
      depthWrite: false, blending: THREE.AdditiveBlending, sizeAttenuation: true,
    }));
    this.embers.frustumCulled = false;
    scene.add(this.embers);
    this.intensity = 0;       // 0..1, driven by temporal blend
  }

  setIntensity(t) { this.intensity = THREE.MathUtils.clamp(t, 0, 1); }

  update(dt, focus) {
    this.points.material.opacity = 0.75 * this.intensity;
    this.embers.material.opacity = 0.9 * this.intensity;
    if (this.intensity <= 0.001) return;
    const fx = focus ? focus.x : 0, fz = focus ? focus.z : 0;
    const p = this.points.geometry.attributes.position.array;
    for (let i = 0; i < this.vel.length; i++) {
      let y = p[i * 3 + 1] - this.vel[i] * dt;
      p[i * 3] += Math.sin(y * 0.5 + i) * dt * 0.3;   // drift
      if (y < 0) { y = this.height; p[i * 3] = fx + (Math.random() - 0.5) * this.area; p[i * 3 + 2] = fz + (Math.random() - 0.5) * this.area; }
      p[i * 3 + 1] = y;
    }
    this.points.geometry.attributes.position.needsUpdate = true;
    const e = this.embers.geometry.attributes.position.array;
    for (let i = 0; i < this.evel.length; i++) {
      let y = e[i * 3 + 1] - this.evel[i] * dt;
      e[i * 3] += Math.sin(y + i) * dt * 0.6;
      if (y < 0) { y = this.height * 0.6; e[i * 3] = fx + (Math.random() - 0.5) * this.area; e[i * 3 + 2] = fz + (Math.random() - 0.5) * this.area; }
      e[i * 3 + 1] = y;
    }
    this.embers.geometry.attributes.position.needsUpdate = true;
  }
}
