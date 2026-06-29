// ASHFALL — the time mechanic. Toggling flips the world Zenith <-> Fall:
// structural meshes swap material/visibility, and the whole mood (sun, fog,
// exposure, sky, ashfall, audio) blends across.
import * as THREE from 'three';

const MOOD = {
  ZENITH: { sun: 0xfff0d8, sunI: 3.2, fog: 0xc9d6e6, fogN: 90, fogF: 320, hemi: 0.28, exp: 1.05, ash: 0 },
  FALL:   { sun: 0xff6326, sunI: 1.25, fog: 0x2a1410, fogN: 16, fogF: 120, hemi: 0.10, exp: 0.9,  ash: 1 },
};

export class Temporal {
  constructor(ctx) {
    Object.assign(this, ctx); // {scene, game, sun, hemi, renderer, fx, audio, envZenith, envFall, bgZenith, bgFall}
    this.state = 'ZENITH';
    this.cur = { ...MOOD.ZENITH, sunC: new THREE.Color(MOOD.ZENITH.sun), fogC: new THREE.Color(MOOD.ZENITH.fog) };
    this.target = MOOD.ZENITH;
    this.listeners = [];
    this._applyMeshes('ZENITH');
    this._applySky('ZENITH');
  }

  onChange(fn) { this.listeners.push(fn); }

  toggle() { this.set(this.state === 'ZENITH' ? 'FALL' : 'ZENITH'); }

  set(state) {
    if (state === this.state) return;
    this.state = state;
    this.target = MOOD[state];
    this._applyMeshes(state);
    this._applySky(state);
    if (this.audio) this.audio.setState(state);
    this.listeners.forEach((fn) => fn(state));
  }

  _applyMeshes(state) {
    const fall = state === 'FALL';
    for (const t of this.game.temporal) {
      if (t.zenithVisible !== undefined || t.fallVisible !== undefined) {
        t.mesh.visible = fall ? (t.fallVisible ?? true) : (t.zenithVisible ?? true);
      }
      if (t.zenithMat && t.fallMat) {
        t.mesh.material = fall ? t.fallMat : t.zenithMat;
      }
    }
  }

  _applySky(state) {
    const fall = state === 'FALL';
    this.scene.environment = fall ? this.envFall : this.envZenith;
    this.scene.background = fall ? this.bgFall : this.bgZenith;
  }

  update(dt) {
    const k = Math.min(1, dt * 2.2);
    const T = this.target;
    this.cur.sunC.lerp(new THREE.Color(T.sun), k);
    this.cur.fogC.lerp(new THREE.Color(T.fog), k);
    this.cur.sunI += (T.sunI - this.cur.sunI) * k;
    this.cur.fogN += (T.fogN - this.cur.fogN) * k;
    this.cur.fogF += (T.fogF - this.cur.fogF) * k;
    this.cur.hemi += (T.hemi - this.cur.hemi) * k;
    this.cur.exp += (T.exp - this.cur.exp) * k;
    this.cur.ash += (T.ash - this.cur.ash) * k;

    this.sun.color.copy(this.cur.sunC);
    this.sun.intensity = this.cur.sunI;
    this.hemi.intensity = this.cur.hemi;
    this.renderer.toneMappingExposure = this.cur.exp;
    if (this.scene.fog) {
      this.scene.fog.color.copy(this.cur.fogC);
      this.scene.fog.near = this.cur.fogN;
      this.scene.fog.far = this.cur.fogF;
    }
    if (this.fx) this.fx.setIntensity(this.cur.ash);
  }
}
