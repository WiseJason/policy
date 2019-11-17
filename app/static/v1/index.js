// $(function(){
//     var flag=true;
//       $('#search').on('compositionstart',function(){
//             flag = false;
//         })
//         $('#search').on('compositionend',function(){
//             flag = true;
//         })
//
//
//     $('#search').on('input ',function(evt){
//             setTimeout(function(){
//                 if(flag){
//
//  // ChangeCoords(); //控制查询结果div坐标
//     var k = window.event ? evt.keyCode : evt.which;
//     //输入框的id为txt_search，这里监听输入框的keyup事件
//     //不为空 && 不为上箭头或下箭头或回车
//     if ($("#txt_search").val() != "" && k != 38 && k != 40 && k != 13) {
//      $.ajax({
//          type: 'Post',
//          //async: false, //同步执行，不然会有问题
//          dataType: "json",
//          url: "/tips", //提交的页面/方法名
//          data: JSON.stringify({"tips":$("#search").val()}),  //参数（如果没有参数：null）
//          contentType: "application/json; charset=utf-8",
//          error: function (msg) {//请求失败处理函数
//              alert("数据加载失败");
//          }
//      })}




























//
//                 }
//             },0)})
//
// })
//
//
//
// function ChangeCoords() {
//    // var left = $("#txt_search")[0].offsetLeft; //获取距离最左端的距离，像素，整型
//    // var top = $("#txt_search")[0].offsetTop + 26; //获取距离最顶端的距离，像素，整型（20为搜索输入框的高度）
//    var left = $("#search").position().left; //获取距离最左端的距离，像素，整型
//    var top = $("#search").position().top + 20; ; //获取距离最顶端的距离，像素，整型（20为搜索输入框的高度）
//    $("#searchresult").css("left", left + "px"); //重新定义CSS属性
//    $("#searchresult").css("top", top + "px"); //同上
//   }