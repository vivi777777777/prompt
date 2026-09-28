// 菜单交互：一级/二级菜单头点击直接跳转到对应默认页，三级子菜单常驻展开
(function () {
  var navMap = {
    '基础信息': 'list_server.html',
    '模型服务器': 'list_server.html',
    '模型': 'mode_list.html'
  };
  document.querySelectorAll('.menu-l1 > .menu-link, .menu-l2 > .menu-link').forEach(function (link) {
    if (link.tagName === 'A') return; // 已是 <a> 的（如 提示词调试）直接跳转
    var label = link.textContent.replace('▶', '').trim();
    var target = navMap[label];
    if (!target) return;
    link.addEventListener('click', function () {
      window.location.href = target;
    });
  });
})();
