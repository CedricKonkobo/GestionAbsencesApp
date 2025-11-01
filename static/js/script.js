window.startQRScan = function (hiddenInputId, formId, prefix) {
  const video   = document.getElementById('video');
  const canvas  = document.getElementById('canvas');
  const ctx     = canvas.getContext('2d');
  const input   = document.getElementById(hiddenInputId);
  const form    = document.getElementById(formId);
  let   scanned = false;          // blocage une seule fois

  navigator.mediaDevices.getUserMedia({ video: { facingMode: "environment" } })
    .then(stream => {
      video.srcObject = stream;
      requestAnimationFrame(tick);
    })
    .catch(err => alert("Caméra inaccessible : " + err));

  function tick() {
    if (scanned) return;          // on a déjà lu → on arrête
    if (video.readyState === video.HAVE_ENOUGH_DATA) {
      canvas.width  = video.videoWidth;
      canvas.height = video.videoHeight;
      ctx.drawImage(video, 0, 0);
      const imageData = ctx.getImageData(0, 0, canvas.width, canvas.height);
      const code = jsQR(imageData.data, canvas.width, canvas.height);
      if (code && code.data.startsWith(prefix)) {
        scanned = true;           // 1 seul envoi
        input.value = code.data;
        form.submit();            // envoi unique
        // on coupe la caméra
        video.srcObject.getTracks().forEach(t => t.stop());
        video.style.display = 'none';
        return;
      }
    }
    requestAnimationFrame(tick);
  }
};