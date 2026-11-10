(() => {
const id = window.SITE_CONFIG?.ga4Id;
const button = document.querySelector('#analytics-consent');
const status = document.querySelector('#analytics-status');
let enabled = false;
button.addEventListener('click', () => {
 if (enabled) { location.reload(); return; }
 if (!/^G-[A-Z0-9]+$/.test(id || '')) { status.textContent = '站长尚未配置统计服务'; return; }
 window.dataLayer = window.dataLayer || [];
 window.gtag = function(){dataLayer.push(arguments)};
 gtag('js', new Date()); gtag('config', id, {send_page_view:true});
 const script = document.createElement('script'); script.async = true;
 script.src = 'https://www.googletagmanager.com/gtag/js?id=' + encodeURIComponent(id);
 document.head.append(script); enabled = true;
 status.textContent = '本页统计已允许（Google Analytics）'; button.textContent = '停止统计并刷新';
});
document.querySelectorAll('a.download[download]').forEach(a => a.addEventListener('click', () => {
 if (enabled) gtag('event', 'resource_download_click', {file_name:a.download, link_url:a.href, transport_type:'beacon'});
}));
})();
