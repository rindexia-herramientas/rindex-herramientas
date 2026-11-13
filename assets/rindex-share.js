/* Rindex — botón "Compartir por WhatsApp" + accesos a redes.
   Se incluye en cada herramienta con <script src="../assets/rindex-share.js" defer></script>.
   El resultado solo se comparte si la persona tilda "Incluir mi resultado" (por defecto, no). */
(function(){
  var REDES = [
    {n:'Instagram', u:'https://www.instagram.com/rindex.ia/', c:'#E1306C',
     svg:'<path d="M12 7a5 5 0 1 0 0 10 5 5 0 0 0 0-10zm0 8.2a3.2 3.2 0 1 1 0-6.4 3.2 3.2 0 0 1 0 6.4zM17.3 5.5a1.2 1.2 0 1 0 0 2.4 1.2 1.2 0 0 0 0-2.4zM12 3.8c2.7 0 3 0 4 .1 2.7.1 4 1.4 4.1 4.1.1 1 .1 1.3.1 4s0 3-.1 4c-.1 2.7-1.4 4-4.1 4.1-1 .1-1.3.1-4 .1s-3 0-4-.1c-2.7-.1-4-1.4-4.1-4.1-.1-1-.1-1.3-.1-4s0-3 .1-4C3.9 5.3 5.3 4 8 3.9c1-.1 1.3-.1 4-.1zM12 2C9.3 2 8.9 2 7.9 2.1 4.2 2.2 2.2 4.2 2.1 7.9 2 8.9 2 9.3 2 12s0 3.1.1 4.1c.1 3.7 2.1 5.7 5.8 5.8 1 .1 1.4.1 4.1.1s3.1 0 4.1-.1c3.7-.1 5.7-2.1 5.8-5.8.1-1 .1-1.4.1-4.1s0-3.1-.1-4.1c-.1-3.7-2.1-5.7-5.8-5.8C15.1 2 14.7 2 12 2z"/>'},
    {n:'TikTok', u:'https://www.tiktok.com/@rindex91', c:'#111',
     svg:'<path d="M16.6 2h-3.3v13.2a2.9 2.9 0 1 1-2-2.8V9a6.2 6.2 0 1 0 5.3 6.2V8.6a7.6 7.6 0 0 0 4.4 1.4V6.7a4.4 4.4 0 0 1-4.4-4.4z"/>'},
    {n:'LinkedIn', u:'https://www.linkedin.com/in/rindex-ia-871452437/', c:'#0A66C2',
     svg:'<path d="M4.98 3.5a2.5 2.5 0 1 1 0 5 2.5 2.5 0 0 1 0-5zM3 9.5h4V21H3zM9.5 9.5h3.8v1.6h.1c.5-1 1.8-2 3.8-2 4 0 4.8 2.6 4.8 6V21h-4v-5.1c0-1.2 0-2.8-1.7-2.8s-2 1.3-2 2.7V21h-4z"/>'},
    {n:'Blog', u:'https://rindexia.com/', c:'#6C4CE0',
     svg:'<path d="M12 2a10 10 0 1 0 0 20 10 10 0 0 0 0-20zm6.9 6h-3a15.6 15.6 0 0 0-1.4-3.9A8 8 0 0 1 18.9 8zM12 4c.8 1.2 1.5 2.5 1.9 4h-3.8c.4-1.5 1.1-2.8 1.9-4zM4.3 14a8 8 0 0 1 0-4h3.4a16.5 16.5 0 0 0 0 4zm.8 2h3a15.6 15.6 0 0 0 1.4 3.9A8 8 0 0 1 5.1 16zm3-8h-3a8 8 0 0 1 4.4-3.9C8.9 5.3 8.4 6.6 8.1 8zM12 20c-.8-1.2-1.5-2.5-1.9-4h3.8c-.4 1.5-1.1 2.8-1.9 4zm2.3-6H9.7a14.7 14.7 0 0 1 0-4h4.6a14.7 14.7 0 0 1 0 4zm.2 5.9c.6-1.2 1.1-2.5 1.4-3.9h3a8 8 0 0 1-4.4 3.9zm1.8-5.9a16.5 16.5 0 0 0 0-4h3.4a8 8 0 0 1 0 4z"/>'}
  ];

  function txt(sel){ var e=document.querySelector(sel); return e ? (e.textContent||'').trim() : ''; }
  function vale(v){ return v && v!=='—' && !/^\$\s*0,00$/.test(v) && v!=='$ 0'; }

  var HERRAMIENTAS = {
    '': {msg:'Hice un recibo de sueldo de Comercio gratis y en PDF con el Liquidador de Rindex 👇',
         res:function(){ var v=txt('.neto-box .val'); return vale(v)?'Neto a percibir: '+v:''; }},
    'calculadora-sueldo': {msg:'Calculé mi sueldo de Comercio en un minuto con esta calculadora gratis 👇',
         res:function(){ var v=txt('#out_neto'); return vale(v)?'Me dio un sueldo neto de '+v:''; }},
    'despidos': {msg:'¿Te despidieron o te quieren despedir? Con esta calculadora gratis sabés cuánto te corresponde 👇',
         res:function(){ var v=txt('#out_total'); return vale(v)?'A mí me dio un total estimado de '+v:''; }},
    'monotributo': {msg:'Averiguá en qué categoría de monotributo estás y cuánto pagás por mes, gratis 👇',
         res:function(){ var l=txt('#out_letra'), c=txt('#out_cuota'); return (vale(l)&&vale(c))?'Me dio categoría '+l+', cuota de '+c+' por mes':''; }},
    'vencimientos': {msg:'Mirá el calendario de vencimientos impositivos según tu CUIT (monotributo, IVA, autónomos y más), gratis 👇'},
    'control-costos': {msg:'Calculá el costo y el margen de ganancia de tus productos gratis, con reporte en PDF 👇'},
    'convertidor': {msg:'Convertí, uní, dividí y comprimí PDFs e imágenes gratis y sin subir nada a internet 👇'}
  };

  var seg = (location.pathname.replace(/^\/rindex-herramientas\/?/,'').replace(/^\//,'').split('/')[0]||'');
  var cfg = HERRAMIENTAS[seg] || {msg:'Herramientas gratis para tu pyme y tu sueldo, de Rindex 👇'};

  function link(){
    var base = 'https://herramientas.rindexia.com/' + (seg ? seg+'/' : '');
    return base + '?utm_source=whatsapp&utm_medium=compartir';
  }
  function contar(nombre){
    try{ if(window.goatcounter && window.goatcounter.count){
      window.goatcounter.count({path:'compartir/'+(seg||'liquidador')+' · '+nombre, title:'compartir', event:true}); } }catch(e){}
  }

  var css = ''
  + '.rx-share-btn{position:fixed;right:16px;bottom:52px;z-index:100000;display:flex;align-items:center;gap:8px;'
  + 'background:#25D366;color:#fff;border:0;border-radius:999px;padding:11px 16px;font:600 14px "Poppins","Segoe UI",Arial,sans-serif;'
  + 'box-shadow:0 4px 14px rgba(0,0,0,.25);cursor:pointer;transition:transform .15s}'
  + '.rx-share-btn:hover{transform:translateY(-2px)}'
  + '.rx-share-btn svg{width:20px;height:20px;fill:#fff}'
  + '.rx-share-panel{position:fixed;right:16px;bottom:104px;z-index:100001;width:290px;max-width:calc(100vw - 32px);background:#fff;color:#1B1740;'
  + 'border-radius:14px;box-shadow:0 10px 30px rgba(27,23,64,.3);padding:16px;font:14px "Poppins","Segoe UI",Arial,sans-serif;display:none}'
  + '.rx-share-panel.on{display:block}'
  + '.rx-share-panel h4{margin:0 0 6px;font-size:15px}'
  + '.rx-share-panel p{margin:0 0 10px;font-size:12.5px;color:#55507a;line-height:1.4}'
  + '.rx-share-panel label{display:flex;gap:8px;align-items:center;font-size:12.5px;margin:0 0 10px;cursor:pointer}'
  + '.rx-share-go{display:block;width:100%;background:#25D366;color:#fff;border:0;border-radius:10px;padding:10px;font-weight:600;font-size:14px;cursor:pointer;font-family:inherit}'
  + '.rx-share-sep{border:0;border-top:1px solid #e6e3f3;margin:14px 0 10px}'
  + '.rx-redes{display:flex;gap:10px;justify-content:center}'
  + '.rx-redes a{width:38px;height:38px;border-radius:50%;display:flex;align-items:center;justify-content:center}'
  + '.rx-redes svg{width:19px;height:19px;fill:#fff}'
  + '.rx-x{position:absolute;top:8px;right:10px;background:none;border:0;font-size:18px;color:#8a85a8;cursor:pointer}'
  + '@media print{.rx-share-btn,.rx-share-panel{display:none!important}}';

  var WA = '<svg viewBox="0 0 24 24"><path d="M17.5 14.4c-.3-.1-1.8-.9-2-1-.3-.1-.5-.1-.7.1-.2.3-.8 1-.9 1.2-.2.2-.3.2-.6.1-.3-.1-1.3-.5-2.4-1.5-.9-.8-1.5-1.8-1.7-2.1-.2-.3 0-.5.1-.6l.4-.5c.2-.2.2-.3.3-.5.1-.2 0-.4 0-.5l-.9-2.2c-.2-.6-.5-.5-.7-.5h-.6c-.2 0-.5.1-.8.4-.3.3-1 1-1 2.5s1.1 2.9 1.2 3.1c.1.2 2.1 3.2 5.1 4.5.7.3 1.3.5 1.7.6.7.2 1.4.2 1.9.1.6-.1 1.8-.7 2-1.4.2-.7.2-1.3.2-1.4-.1-.1-.3-.2-.6-.3zM12 21.8c-1.8 0-3.5-.5-5-1.4l-.4-.2-3.7 1 1-3.6-.2-.4A9.8 9.8 0 1 1 12 21.8zm0-21.6A11.8 11.8 0 0 0 1.9 18l-1.7 6 6.2-1.6A11.8 11.8 0 1 0 12 .2z"/></svg>';

  function init(){
    var st=document.createElement('style'); st.textContent=css; document.head.appendChild(st);

    var btn=document.createElement('button');
    btn.className='rx-share-btn no-print'; btn.type='button';
    btn.setAttribute('aria-label','Compartir por WhatsApp');
    btn.innerHTML=WA+'<span>Compartir</span>';

    var p=document.createElement('div'); p.className='rx-share-panel no-print';
    var redes=REDES.map(function(r){
      return '<a href="'+r.u+'" target="_blank" rel="noopener" title="Seguí a Rindex en '+r.n+'" style="background:'+r.c+'" data-red="'+r.n+'"><svg viewBox="0 0 24 24">'+r.svg+'</svg></a>';
    }).join('');
    p.innerHTML='<button class="rx-x" type="button" aria-label="Cerrar">×</button>'
      +'<h4>¿Le sirve a alguien más?</h4>'
      +'<p>Mandale esta herramienta gratis por WhatsApp a quien la pueda necesitar.</p>'
      +(cfg.res?'<label><input type="checkbox" class="rx-incl"> Incluir mi resultado</label>':'')
      +'<button class="rx-share-go" type="button">Enviar por WhatsApp</button>'
      +'<hr class="rx-share-sep"><p style="text-align:center;margin-bottom:8px">Seguí a Rindex para más herramientas</p>'
      +'<div class="rx-redes">'+redes+'</div>';

    document.body.appendChild(p); document.body.appendChild(btn);

    btn.addEventListener('click',function(){ p.classList.toggle('on'); if(p.classList.contains('on')) contar('abrir'); });
    p.querySelector('.rx-x').addEventListener('click',function(){ p.classList.remove('on'); });
    p.querySelector('.rx-share-go').addEventListener('click',function(){
      var partes=[cfg.msg];
      var incl=p.querySelector('.rx-incl');
      if(incl && incl.checked){ var r=cfg.res(); if(r) partes.push(r); }
      partes.push(link());
      contar(incl && incl.checked ? 'whatsapp con resultado' : 'whatsapp');
      window.open('https://wa.me/?text='+encodeURIComponent(partes.join('\n\n')),'_blank','noopener');
    });
    Array.prototype.forEach.call(p.querySelectorAll('.rx-redes a'),function(a){
      a.addEventListener('click',function(){ contar('seguir '+a.getAttribute('data-red')); });
    });
  }
  if(document.readyState==='loading') document.addEventListener('DOMContentLoaded',init); else init();
})();
