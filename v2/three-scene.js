(() => {
  const boot = () => {
    const host = document.getElementById('three-tracking');
    if (!host || !window.THREE) return;

    const THREE = window.THREE;
    const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;
    const scene = new THREE.Scene();
    scene.fog = new THREE.FogExp2(0x071522, 0.012);

    const camera = new THREE.PerspectiveCamera(46, 1, 0.1, 900);
    camera.position.set(18, 13, 24);
    camera.lookAt(0, 0, 0);

    const renderer = new THREE.WebGLRenderer({ antialias: true, alpha: true, powerPreference: 'high-performance' });
    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 1.6));
    renderer.setSize(host.clientWidth || 900, host.clientHeight || 500);
    renderer.outputColorSpace = THREE.SRGBColorSpace;
    renderer.toneMapping = THREE.ACESFilmicToneMapping;
    renderer.toneMappingExposure = 1.08;
    host.appendChild(renderer.domElement);

    const hemi = new THREE.HemisphereLight(0x9fd5ff, 0x06101c, 1.5);
    scene.add(hemi);
    const key = new THREE.DirectionalLight(0xffd0a8, 2.2);
    key.position.set(-18, 28, 12);
    scene.add(key);
    const rim = new THREE.PointLight(0xf25a22, 9, 80, 2);
    rim.position.set(0, 7, -10);
    scene.add(rim);

    const ocean = new THREE.Mesh(
      new THREE.PlaneGeometry(190, 190, 70, 70),
      new THREE.MeshStandardMaterial({ color: 0x082944, roughness: 0.34, metalness: 0.28, transparent: true, opacity: 0.94 })
    );
    ocean.rotation.x = -Math.PI / 2;
    ocean.position.y = -0.75;
    scene.add(ocean);

    const oceanPos = ocean.geometry.attributes.position;
    const oceanBase = new Float32Array(oceanPos.array);

    const grid = new THREE.GridHelper(150, 30, 0x1c6a96, 0x123b55);
    grid.position.y = -0.66;
    grid.material.transparent = true;
    grid.material.opacity = 0.22;
    scene.add(grid);

    const starsGeo = new THREE.BufferGeometry();
    const starCount = window.innerWidth < 700 ? 350 : 700;
    const starArr = new Float32Array(starCount * 3);
    for (let i = 0; i < starCount; i++) {
      starArr[i * 3] = (Math.random() - 0.5) * 150;
      starArr[i * 3 + 1] = Math.random() * 55 + 2;
      starArr[i * 3 + 2] = (Math.random() - 0.5) * 150;
    }
    starsGeo.setAttribute('position', new THREE.BufferAttribute(starArr, 3));
    const stars = new THREE.Points(starsGeo, new THREE.PointsMaterial({ color: 0xaedcff, size: 0.18, transparent: true, opacity: 0.55 }));
    scene.add(stars);

    const ringMat = new THREE.MeshBasicMaterial({ color: 0xf25a22, transparent: true, opacity: 0.24, side: THREE.DoubleSide });
    [5, 9, 14].forEach((r, i) => {
      const ring = new THREE.Mesh(new THREE.RingGeometry(r - 0.035, r + 0.035, 96), ringMat.clone());
      ring.rotation.x = -Math.PI / 2;
      ring.position.y = -0.58 + i * 0.01;
      scene.add(ring);
    });

    const sweep = new THREE.Mesh(
      new THREE.CircleGeometry(13, 48, -0.15, Math.PI / 3.3),
      new THREE.MeshBasicMaterial({ color: 0xf25a22, transparent: true, opacity: 0.08, side: THREE.DoubleSide })
    );
    sweep.rotation.x = -Math.PI / 2;
    sweep.position.y = -0.52;
    scene.add(sweep);

    const beacon = new THREE.Mesh(
      new THREE.CylinderGeometry(0.03, 2.7, 13, 32, 1, true),
      new THREE.MeshBasicMaterial({ color: 0xf25a22, transparent: true, opacity: 0.07, side: THREE.DoubleSide, blending: THREE.AdditiveBlending })
    );
    beacon.position.set(0, 6, 0);
    scene.add(beacon);

    const vessel = new THREE.Group();
    vessel.position.y = 0.05;
    scene.add(vessel);

    const hullShape = new THREE.Shape();
    hullShape.moveTo(-2.5, 0); hullShape.lineTo(1.9, 0); hullShape.lineTo(2.55, 0.65); hullShape.lineTo(-1.85, 0.65); hullShape.closePath();
    const hull = new THREE.Mesh(new THREE.ExtrudeGeometry(hullShape, { depth: 0.9, bevelEnabled: true, bevelSegments: 3, bevelSize: 0.12, bevelThickness: 0.1 }), new THREE.MeshStandardMaterial({ color: 0xe9f2f8, roughness: 0.28, metalness: 0.4 }));
    hull.rotation.y = Math.PI / 2;
    hull.rotation.z = Math.PI;
    hull.position.set(0, 0, -0.45);
    vessel.add(hull);

    const cabin = new THREE.Mesh(new THREE.BoxGeometry(2.3, 1.15, 1.7), new THREE.MeshStandardMaterial({ color: 0x0a3157, roughness: 0.22, metalness: 0.45, emissive: 0x061a2d, emissiveIntensity: 0.5 }));
    cabin.position.set(-0.15, 1.05, 0);
    vessel.add(cabin);
    const roof = new THREE.Mesh(new THREE.BoxGeometry(2.6, 0.18, 1.95), new THREE.MeshStandardMaterial({ color: 0xf25a22, roughness: 0.24, metalness: 0.35 }));
    roof.position.set(-0.15, 1.72, 0);
    vessel.add(roof);

    const mast = new THREE.Mesh(new THREE.CylinderGeometry(0.055, 0.055, 3.1, 12), new THREE.MeshStandardMaterial({ color: 0xdce7ee, metalness: 0.8, roughness: 0.2 }));
    mast.position.set(-0.15, 3.15, 0);
    vessel.add(mast);
    const antenna = new THREE.Mesh(new THREE.CylinderGeometry(0.025, 0.025, 1.3, 8), new THREE.MeshBasicMaterial({ color: 0xf25a22 }));
    antenna.position.set(-0.15, 5.05, 0);
    vessel.add(antenna);

    const lamp = new THREE.Mesh(new THREE.SphereGeometry(0.16, 16, 16), new THREE.MeshBasicMaterial({ color: 0xf25a22 }));
    lamp.position.set(-0.15, 4.9, 0);
    vessel.add(lamp);
    const lampLight = new THREE.PointLight(0xf25a22, 5, 18, 2);
    lampLight.position.copy(lamp.position);
    vessel.add(lampLight);

    const trail = [];
    const trailLine = new THREE.Line(new THREE.BufferGeometry(), new THREE.LineBasicMaterial({ color: 0xf25a22, transparent: true, opacity: 0.78 }));
    scene.add(trailLine);

    const target = new THREE.Mesh(new THREE.RingGeometry(0.45, 0.56, 32), new THREE.MeshBasicMaterial({ color: 0x66d9ff, transparent: true, opacity: 0.9, side: THREE.DoubleSide }));
    target.rotation.x = -Math.PI / 2;
    target.position.y = -0.48;
    scene.add(target);

    const geofence = new THREE.Mesh(new THREE.CylinderGeometry(12, 12, 4.2, 64, 1, true), new THREE.MeshBasicMaterial({ color: 0x66d9ff, transparent: true, opacity: 0.035, wireframe: true }));
    geofence.position.y = 1.3;
    scene.add(geofence);

    const hud = document.createElement('div');
    hud.className = 'three-hud';
    hud.innerHTML = '<div class="three-chip"><span>3D COMMAND VIEW</span><b id="three-state">AWAITING TELEMETRY</b></div><div class="three-readout"><span>LAT <b id="three-lat">--</b></span><span>LON <b id="three-lon">--</b></span><span>ALT <b id="three-alt">SEA</b></span></div><div class="three-scan">RADAR / LIVE NODE</div>';
    host.appendChild(hud);

    const empty = document.createElement('div');
    empty.className = 'three-empty';
    empty.innerHTML = '<strong>3D TELEMETRY LAYER</strong><span>Connecting to vessel node…</span>';
    host.appendChild(empty);

    let origin = null;
    let yaw = 0;
    let pitch = 0.35;
    let distance = 25;
    let desiredX = 0, desiredZ = 0;
    let alert = false;
    let last = performance.now();

    const setTelemetry = (d) => {
      if (!d) return;
      const lat = Number(d.latitude), lon = Number(d.longitude);
      if (!Number.isFinite(lat) || !Number.isFinite(lon)) return;
      if (!origin) origin = { lat, lon };
      const scale = 90000;
      desiredX = (lon - origin.lon) * Math.cos(origin.lat * Math.PI / 180) * scale;
      desiredZ = -(lat - origin.lat) * scale;
      desiredX = THREE.MathUtils.clamp(desiredX, -38, 38);
      desiredZ = THREE.MathUtils.clamp(desiredZ, -38, 38);
      const status = String(d.status || '').toUpperCase();
      alert = d.isAlertActive === true || status.includes('SOS') || status.includes('ALERT');
      document.getElementById('three-lat').textContent = lat.toFixed(6);
      document.getElementById('three-lon').textContent = lon.toFixed(6);
      document.getElementById('three-state').textContent = alert ? 'SOS / ALERT' : 'TELEMETRY LIVE';
      document.querySelector('.three-chip').classList.toggle('danger', alert);
      empty.classList.add('hidden');
      trail.push(new THREE.Vector3(desiredX, -0.48, desiredZ));
      if (trail.length > 120) trail.shift();
      const pos = new Float32Array(trail.length * 3);
      trail.forEach((p, i) => { pos[i * 3] = p.x; pos[i * 3 + 1] = p.y; pos[i * 3 + 2] = p.z; });
      trailLine.geometry.dispose();
      trailLine.geometry = new THREE.BufferGeometry();
      trailLine.geometry.setAttribute('position', new THREE.BufferAttribute(pos, 3));
    };

    if (window.connectTelemetry) window.connectTelemetry(setTelemetry);

    const resize = () => {
      const w = host.clientWidth || 900, h = host.clientHeight || 520;
      camera.aspect = w / h; camera.updateProjectionMatrix(); renderer.setSize(w, h);
    };
    window.addEventListener('resize', resize);
    resize();

    host.addEventListener('pointermove', (e) => {
      if (e.pointerType === 'touch') return;
      const r = host.getBoundingClientRect();
      yaw = ((e.clientX - r.left) / r.width - 0.5) * 0.55;
      pitch = 0.28 + ((e.clientY - r.top) / r.height - 0.5) * 0.25;
    });
    host.addEventListener('wheel', (e) => {
      e.preventDefault();
      distance = THREE.MathUtils.clamp(distance + e.deltaY * 0.015, 15, 38);
    }, { passive: false });

    const animate = (now) => {
      const dt = Math.min((now - last) / 1000, 0.05); last = now;
      const t = now * 0.001;
      const p = oceanPos.array;
      for (let i = 0; i < p.length; i += 3) {
        const x = oceanBase[i], z = oceanBase[i + 1];
        p[i + 2] = oceanBase[i + 2] + Math.sin(x * 0.15 + t * 1.4) * 0.12 + Math.cos(z * 0.11 + t) * 0.09;
      }
      oceanPos.needsUpdate = true;
      ocean.geometry.computeVertexNormals();
      sweep.rotation.z = t * 0.8;
      geofence.rotation.y = t * 0.12;
      stars.rotation.y = t * 0.008;
      target.position.x += (desiredX - target.position.x) * Math.min(1, dt * 4);
      target.position.z += (desiredZ - target.position.z) * Math.min(1, dt * 4);
      vessel.position.x += (desiredX - vessel.position.x) * Math.min(1, dt * 3);
      vessel.position.z += (desiredZ - vessel.position.z) * Math.min(1, dt * 3);
      vessel.rotation.y = Math.sin(t * 0.55) * 0.025;
      lamp.scale.setScalar(1 + Math.sin(t * 5) * 0.12);
      beacon.material.opacity = alert ? 0.12 + Math.sin(t * 6) * 0.06 : 0.045;
      geofence.material.opacity = alert ? 0.075 : 0.035;
      if (!reduceMotion) camera.position.lerp(new THREE.Vector3(Math.sin(yaw) * distance, 10 + pitch * 8, Math.cos(yaw) * distance), 0.045);
      camera.lookAt(vessel.position.x * 0.18, 0.5, vessel.position.z * 0.18);
      renderer.render(scene, camera);
      requestAnimationFrame(animate);
    };
    requestAnimationFrame(animate);
  };

  const loadThree = () => {
    if (window.THREE) return boot();
    const s = document.createElement('script');
    s.src = 'https://cdn.jsdelivr.net/npm/three@0.179.1/build/three.min.js';
    s.onload = boot;
    s.onerror = () => document.getElementById('three-tracking')?.classList.add('fallback');
    document.head.appendChild(s);
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', loadThree); else loadThree();
})();
