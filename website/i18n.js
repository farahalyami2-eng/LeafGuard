// LeafGuard i18n — English / Chinese Simplified / Arabic
// t(key)            → translated string for current language
// setLanguage(lang) → switch + persist + re-render
// applyTranslations()→ stamp all [data-i18n] elements

const TRANSLATIONS = {
  en: {
    // Nav
    nav_home:'Home', nav_sim:'Simulation', nav_shop:'Shop',
    nav_chat:'AI Advisor', nav_dashboard:'Dashboard', nav_orders:'My Orders',
    nav_signout:'Sign Out',
    // Location modal
    modal_loc_title:'Allow Location Access',
    modal_loc_desc:'LeafGuard uses your location to provide climate-specific advice, irrigation schedules, and product recommendations for your region.',
    modal_loc_allow:'Allow Location', modal_loc_skip:'Skip for now',
    // Hero
    hero_tag:'AI-Powered Agricultural Intelligence',
    hero_title:'Grow smarter.\nFarm with data.',
    hero_sub:'LeafGuard combines 3D simulation, AI diagnostics, and precision agronomy to help farmers make better decisions — from soil to harvest.',
    hero_btn_sim:'Try Simulation', hero_btn_shop:'Browse Products',
    // Stats
    stat_products:'Products', stat_species:'Plant Species',
    stat_sim:'Simulation', stat_advisor:'AI Advisor',
    // Features section
    feat_label:'Platform Capabilities',
    feat_title:'Everything you need to farm intelligently',
    feat_3d_title:'3D Simulation',
    feat_3d_desc:'Visualize your field in three dimensions. Run growth models, test irrigation scenarios, and predict yield before planting.',
    feat_3d_link:'Launch Simulation',
    feat_ai_title:'AI Advisor',
    feat_ai_desc:'Get expert crop management advice, disease diagnosis, and product recommendations from our AI agronomist — 24/7.',
    feat_ai_link:'Ask a Question',
    feat_shop_title:'Smart Shop',
    feat_shop_desc:'Browse 114+ certified agricultural products — fertilizers, pesticides, and growth regulators — filtered by crop and problem.',
    feat_shop_link:'Browse Products',
    feat_gps_title:'GPS Field Analysis',
    feat_gps_desc:'Map your fields with GPS precision. Identify soil variation zones and optimize resource allocation.',
    feat_gps_link:'View Dashboard',
    feat_dash_title:'Live Dashboard',
    feat_dash_desc:'Monitor plant health, track orders, view simulation runs, and analyze yield trends all in one hub.',
    feat_dash_link:'Open Dashboard',
    feat_disease_title:'Disease Detection',
    feat_disease_desc:'AI-powered plant disease identification. Describe symptoms, get instant diagnosis and treatment recommendations.',
    feat_disease_link:'Diagnose Now',
    // Simulation
    sim_loads:'Simulation loads here',
    sim_connect:'Connect the 3D simulation module to begin',
    // Shop
    shop_category:'Category', shop_subtype:'Sub-type', shop_price:'Price Range (SAR)',
    shop_all:'All', shop_fertilizers:'Fertilizers',
    shop_bio:'Biological Pesticides', shop_chem:'Chemical Pesticides', shop_pgr:'Plant Growth Regulators',
    shop_insect:'Insecticides', shop_fungi:'Fungicides', shop_herb:'Herbicides',
    shop_foliar:'Foliar Nutrients', shop_bacillus:'Bacillus Bio',
    shop_search_ph:'Search products...',
    shop_sort_name:'Sort: Name', shop_sort_type:'Sort: Type',
    shop_sort_asc:'Price: Low to High', shop_sort_desc:'Price: High to Low',
    shop_add:'Add to cart', shop_in_cart:'✓ In cart',
    // Chat sidebar
    chat_topics:'Topics', chat_quick:'Quick Questions', chat_your_loc:'Your Location',
    chat_crop:'Crop Management', chat_disease:'Disease Diagnosis',
    chat_products:'Product Advice', chat_soil:'Soil & Fertilizers',
    chat_water:'Water & Irrigation', chat_weather:'Weather & Climate',
    chat_sim_help:'Simulation Help',
    chat_q1:'Yellow tomato leaves', chat_q2:'Fertilizer for wheat',
    chat_q3:'Pepper irrigation', chat_q4:'Cucumber mildew', chat_q5:'Using 3D simulation',
    chat_ph:'Ask about your crops, diseases, or products...',
    // Chat tips
    tips_title:'LeafGuard AI Advisor',
    tips_sub:'Upload a plant photo or ask a question to get started.',
    tips_1:'Shoot in natural daylight — avoid harsh shadows',
    tips_2:'Fill the frame with the leaf or affected area',
    tips_3:'Hold steady — blurry photos lower accuracy',
    tips_4:'Upload up to 4 images to compare multiple leaves',
    // Low confidence
    low_conf:'Low confidence detected. For better results, try retaking the photo in natural daylight, fill the frame with the leaf, and avoid blur.',
    // Dashboard
    dash_overview:'Overview', dash_fields:'My Fields', dash_orders_nav:'Orders',
    dash_sims:'Simulations', dash_analytics:'Analytics', dash_ai:'AI Advisor',
    kpi_health:'Avg Plant Health', kpi_yield:'Estimated Yield',
    kpi_orders:'Orders This Month', kpi_cart:'Items in Cart',
    kpi_from_sim:'From simulation', kpi_projected:'Projected',
    kpi_last30:'Last 30 days',
    dash_recent:'Recent Orders', dash_activity:'Field Activity',
    // Orders
    orders_label:'My Orders',
    orders_empty_p:'Select an order from the list to track it',
    orders_empty_s:'Your placed orders will appear here',
    tracking_delivery:'Delivery Status', tracking_items:'Order Items',
    // Auth
    auth_tagline:'AI-Powered Agricultural Intelligence',
    auth_signin:'Sign In', auth_signup:'Create Account',
    auth_email:'Email', auth_password:'Password', auth_fullname:'Full Name',
    auth_email_ph:'you@example.com', auth_pass_ph:'••••••••',
    auth_name_ph:'Your full name', auth_pass_min:'Min. 6 characters',
    auth_footer:'LeafGuard · Agricultural Intelligence Platform',
    // JS dynamic
    err_session:'Your session has expired. Please sign in again.',
    err_network:'Network error — please check your connection and try again.',
    cart_empty_title:'Your cart is empty',
    cart_empty_sub:'Add items to get started.',
    checkout_ok:'Order placed! Redirecting to orders...',
    checkout_fail:'Failed to place order.',
    added_to_cart:'✓ Added to cart: ',
    orders_none:'No orders yet.\nAdd items to your cart and checkout!',
  },

  zh: {
    nav_home:'首页', nav_sim:'模拟', nav_shop:'商店',
    nav_chat:'AI 顾问', nav_dashboard:'仪表盘', nav_orders:'我的订单',
    nav_signout:'退出登录',
    modal_loc_title:'允许位置访问',
    modal_loc_desc:'LeafGuard 使用您的位置提供气候建议、灌溉计划和适合您地区的产品推荐。',
    modal_loc_allow:'允许位置', modal_loc_skip:'暂时跳过',
    hero_tag:'AI 驱动的农业智能',
    hero_title:'更智慧地种植。\n用数据耕作。',
    hero_sub:'LeafGuard 结合 3D 模拟、AI 诊断和精准农学，帮助农民从土壤到收获做出更好决策。',
    hero_btn_sim:'试用模拟', hero_btn_shop:'浏览产品',
    stat_products:'产品', stat_species:'植物种类', stat_sim:'3D 模拟', stat_advisor:'AI 顾问',
    feat_label:'平台功能',
    feat_title:'智慧农业，一切尽在掌握',
    feat_3d_title:'3D 模拟',
    feat_3d_desc:'三维可视化您的农田。运行生长模型，测试灌溉方案，在种植前预测产量。',
    feat_3d_link:'启动模拟',
    feat_ai_title:'AI 顾问',
    feat_ai_desc:'全天候获取作物管理建议、病害诊断和产品推荐。',
    feat_ai_link:'提问',
    feat_shop_title:'智能商店',
    feat_shop_desc:'浏览 114+ 种认证农业产品 — 化肥、农药和生长调节剂。',
    feat_shop_link:'浏览产品',
    feat_gps_title:'GPS 田地分析',
    feat_gps_desc:'使用 GPS 精确绘制农田地图，识别土壤变化区域，优化资源配置。',
    feat_gps_link:'查看仪表盘',
    feat_dash_title:'实时仪表盘',
    feat_dash_desc:'在同一中心监控植物健康、跟踪订单、查看模拟运行和分析产量趋势。',
    feat_dash_link:'打开仪表盘',
    feat_disease_title:'病害检测',
    feat_disease_desc:'AI 驱动的植物病害识别。描述症状，立即获得诊断和治疗建议。',
    feat_disease_link:'立即诊断',
    sim_loads:'模拟在此加载', sim_connect:'连接 3D 模拟模块以开始',
    shop_category:'类别', shop_subtype:'子类型', shop_price:'价格范围 (SAR)',
    shop_all:'全部', shop_fertilizers:'化肥', shop_bio:'生物农药',
    shop_chem:'化学农药', shop_pgr:'植物生长调节剂',
    shop_insect:'杀虫剂', shop_fungi:'杀菌剂', shop_herb:'除草剂',
    shop_foliar:'叶面营养', shop_bacillus:'芽孢杆菌生物制剂',
    shop_search_ph:'搜索产品...', shop_sort_name:'排序：名称', shop_sort_type:'排序：类型',
    shop_sort_asc:'价格：从低到高', shop_sort_desc:'价格：从高到低',
    shop_add:'加入购物车', shop_in_cart:'✓ 已加入',
    chat_topics:'话题', chat_quick:'常见问题', chat_your_loc:'您的位置',
    chat_crop:'作物管理', chat_disease:'病害诊断', chat_products:'产品建议',
    chat_soil:'土壤与化肥', chat_water:'水与灌溉', chat_weather:'天气与气候',
    chat_sim_help:'模拟帮助',
    chat_q1:'番茄叶片发黄', chat_q2:'小麦施肥', chat_q3:'辣椒灌溉',
    chat_q4:'黄瓜白粉病', chat_q5:'3D 模拟使用',
    chat_ph:'询问关于您的作物、病害或产品...',
    tips_title:'LeafGuard AI 顾问',
    tips_sub:'上传植物照片或提问以开始。',
    tips_1:'在自然光下拍摄 — 避免强烈阴影',
    tips_2:'用叶片或受影响区域填满画面',
    tips_3:'保持稳定 — 模糊照片会降低准确度',
    tips_4:'最多上传 4 张图片以比较多片叶子',
    low_conf:'检测到低置信度。请在自然光下重新拍照，用叶片填满画面，避免模糊。',
    dash_overview:'概览', dash_fields:'我的田地', dash_orders_nav:'订单',
    dash_sims:'模拟', dash_analytics:'分析', dash_ai:'AI 顾问',
    kpi_health:'平均植物健康', kpi_yield:'预计产量',
    kpi_orders:'本月订单', kpi_cart:'购物车商品',
    kpi_from_sim:'来自模拟', kpi_projected:'预计', kpi_last30:'最近 30 天',
    dash_recent:'最近订单', dash_activity:'田地活动',
    orders_label:'我的订单',
    orders_empty_p:'从列表中选择订单以跟踪',
    orders_empty_s:'您下的订单将显示在这里',
    tracking_delivery:'配送状态', tracking_items:'订单商品',
    auth_tagline:'AI 驱动的农业智能',
    auth_signin:'登录', auth_signup:'创建账户',
    auth_email:'电子邮件', auth_password:'密码', auth_fullname:'全名',
    auth_email_ph:'您的邮箱', auth_pass_ph:'••••••••',
    auth_name_ph:'您的全名', auth_pass_min:'最少 6 个字符',
    auth_footer:'LeafGuard · 农业智能平台',
    err_session:'您的会话已过期，请重新登录。',
    err_network:'网络错误 — 请检查连接后重试。',
    cart_empty_title:'购物车为空', cart_empty_sub:'添加商品以开始。',
    checkout_ok:'下单成功！正在跳转至订单页面...', checkout_fail:'下单失败。',
    added_to_cart:'✓ 已加入购物车：',
    orders_none:'暂无订单。\n将商品加入购物车并结账！',
  },

  ar: {
    nav_home:'الرئيسية', nav_sim:'المحاكاة', nav_shop:'المتجر',
    nav_chat:'المستشار الذكي', nav_dashboard:'لوحة التحكم', nav_orders:'طلباتي',
    nav_signout:'تسجيل الخروج',
    modal_loc_title:'السماح بالوصول إلى الموقع',
    modal_loc_desc:'يستخدم LeafGuard موقعك لتقديم نصائح مناخية وجداول ري وتوصيات منتجات لمنطقتك.',
    modal_loc_allow:'السماح بالموقع', modal_loc_skip:'تخطي الآن',
    hero_tag:'ذكاء اصطناعي للزراعة الذكية',
    hero_title:'ازرع بذكاء.\nاعمل بالبيانات.',
    hero_sub:'يجمع LeafGuard بين المحاكاة ثلاثية الأبعاد والتشخيص الذكي وعلم الزراعة الدقيق لمساعدة المزارعين على اتخاذ قرارات أفضل.',
    hero_btn_sim:'جرب المحاكاة', hero_btn_shop:'تصفح المنتجات',
    stat_products:'منتج', stat_species:'نوع نباتي',
    stat_sim:'محاكاة ثلاثية الأبعاد', stat_advisor:'مستشار ذكي',
    feat_label:'إمكانيات المنصة',
    feat_title:'كل ما تحتاجه للزراعة الذكية',
    feat_3d_title:'المحاكاة ثلاثية الأبعاد',
    feat_3d_desc:'تصور حقلك بثلاثة أبعاد. شغّل نماذج النمو واختبر سيناريوهات الري وتوقع المحصول.',
    feat_3d_link:'ابدأ المحاكاة',
    feat_ai_title:'المستشار الذكي',
    feat_ai_desc:'احصل على نصائح إدارة المحاصيل وتشخيص الأمراض وتوصيات المنتجات على مدار الساعة.',
    feat_ai_link:'اسأل سؤالاً',
    feat_shop_title:'المتجر الذكي',
    feat_shop_desc:'تصفح أكثر من ١١٤ منتجاً زراعياً معتمداً — أسمدة ومبيدات ومنظمات نمو.',
    feat_shop_link:'تصفح المنتجات',
    feat_gps_title:'تحليل الحقل بنظام GPS',
    feat_gps_desc:'ارسم خرائط حقولك بدقة GPS وتعرف على مناطق تباين التربة.',
    feat_gps_link:'عرض لوحة التحكم',
    feat_dash_title:'لوحة التحكم المباشرة',
    feat_dash_desc:'راقب صحة النباتات وتتبع الطلبات وحلّل اتجاهات المحصول في مكان واحد.',
    feat_dash_link:'فتح لوحة التحكم',
    feat_disease_title:'اكتشاف الأمراض',
    feat_disease_desc:'تحديد أمراض النباتات بالذكاء الاصطناعي. صف الأعراض واحصل على تشخيص فوري.',
    feat_disease_link:'تشخيص الآن',
    sim_loads:'المحاكاة تُحمّل هنا', sim_connect:'قم بتوصيل وحدة المحاكاة ثلاثية الأبعاد للبدء',
    shop_category:'الفئة', shop_subtype:'النوع الفرعي', shop_price:'نطاق السعر (ريال)',
    shop_all:'الكل', shop_fertilizers:'الأسمدة', shop_bio:'المبيدات الحيوية',
    shop_chem:'المبيدات الكيميائية', shop_pgr:'منظمات النمو النباتي',
    shop_insect:'مبيدات الحشرات', shop_fungi:'مبيدات الفطريات', shop_herb:'مبيدات الأعشاب',
    shop_foliar:'التغذية الورقية', shop_bacillus:'البكتيريا الحيوية',
    shop_search_ph:'بحث عن منتجات...', shop_sort_name:'ترتيب: الاسم', shop_sort_type:'ترتيب: النوع',
    shop_sort_asc:'السعر: من الأقل', shop_sort_desc:'السعر: من الأعلى',
    shop_add:'أضف للسلة', shop_in_cart:'✓ في السلة',
    chat_topics:'المواضيع', chat_quick:'أسئلة سريعة', chat_your_loc:'موقعك',
    chat_crop:'إدارة المحاصيل', chat_disease:'تشخيص الأمراض', chat_products:'نصائح المنتجات',
    chat_soil:'التربة والأسمدة', chat_water:'المياه والري', chat_weather:'الطقس والمناخ',
    chat_sim_help:'مساعدة المحاكاة',
    chat_q1:'أوراق الطماطم الصفراء', chat_q2:'سماد القمح', chat_q3:'ري الفلفل',
    chat_q4:'البياض الدقيقي على الخيار', chat_q5:'استخدام المحاكاة ثلاثية الأبعاد',
    chat_ph:'اسأل عن محاصيلك أو الأمراض أو المنتجات...',
    tips_title:'مستشار LeafGuard الذكي',
    tips_sub:'ارفع صورة نبات أو اطرح سؤالاً للبدء.',
    tips_1:'التقط في ضوء طبيعي — تجنب الظلال القاسية',
    tips_2:'املأ الإطار بالورقة أو المنطقة المتضررة',
    tips_3:'أبقِ الكاميرا ثابتة — الصور الضبابية تقلل الدقة',
    tips_4:'ارفع حتى ٤ صور لمقارنة أوراق متعددة',
    low_conf:'تم اكتشاف ثقة منخفضة. للنتائج الأفضل، التقط الصورة في ضوء طبيعي مع ملء الإطار بالورقة وتجنب الضبابية.',
    dash_overview:'نظرة عامة', dash_fields:'حقولي', dash_orders_nav:'الطلبات',
    dash_sims:'المحاكاة', dash_analytics:'التحليلات', dash_ai:'المستشار الذكي',
    kpi_health:'متوسط صحة النبات', kpi_yield:'المحصول المتوقع',
    kpi_orders:'طلبات الشهر', kpi_cart:'عناصر السلة',
    kpi_from_sim:'من المحاكاة', kpi_projected:'متوقع', kpi_last30:'آخر ٣٠ يوماً',
    dash_recent:'الطلبات الأخيرة', dash_activity:'نشاط الحقل',
    orders_label:'طلباتي',
    orders_empty_p:'اختر طلباً من القائمة لتتبعه',
    orders_empty_s:'طلباتك الموضوعة ستظهر هنا',
    tracking_delivery:'حالة التوصيل', tracking_items:'عناصر الطلب',
    auth_tagline:'ذكاء اصطناعي للزراعة الذكية',
    auth_signin:'تسجيل الدخول', auth_signup:'إنشاء حساب',
    auth_email:'البريد الإلكتروني', auth_password:'كلمة المرور', auth_fullname:'الاسم الكامل',
    auth_email_ph:'example@domain.com', auth_pass_ph:'••••••••',
    auth_name_ph:'اسمك الكامل', auth_pass_min:'٦ أحرف على الأقل',
    auth_footer:'LeafGuard · منصة الذكاء الزراعي',
    err_session:'انتهت جلستك. الرجاء تسجيل الدخول مجدداً.',
    err_network:'خطأ في الشبكة — يرجى التحقق من الاتصال والمحاولة مرة أخرى.',
    cart_empty_title:'سلتك فارغة', cart_empty_sub:'أضف عناصر للبدء.',
    checkout_ok:'تم تقديم الطلب! جارٍ التحويل للطلبات...', checkout_fail:'فشل تقديم الطلب.',
    added_to_cart:'✓ أضيف للسلة: ',
    orders_none:'لا توجد طلبات بعد.\nأضف عناصر للسلة وأتم الشراء!',
  },
};

let currentLang = localStorage.getItem('lg_lang') || 'en';

function t(key) {
  return (TRANSLATIONS[currentLang]?.[key]) ?? (TRANSLATIONS.en[key]) ?? key;
}

function setLanguage(lang) {
  if (!TRANSLATIONS[lang]) return;
  currentLang = lang;
  localStorage.setItem('lg_lang', lang);
  document.documentElement.lang = lang;
  document.documentElement.dir = lang === 'ar' ? 'rtl' : 'ltr';
  applyTranslations();
  document.querySelectorAll('.lang-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.lang === lang)
  );
}

function applyTranslations() {
  document.querySelectorAll('[data-i18n]').forEach(el => {
    const v = t(el.dataset.i18n);
    if (v !== undefined) el.textContent = v;
  });
  document.querySelectorAll('[data-i18n-ph]').forEach(el => {
    const v = t(el.dataset.i18nPh);
    if (v) el.placeholder = v;
  });
  document.querySelectorAll('[data-i18n-html]').forEach(el => {
    const key = el.dataset.i18nHtml;
    const v = t(key);
    if (v) el.innerHTML = v.replace(/\n/g, '<br>');
  });
}

// Init on DOMContentLoaded
document.addEventListener('DOMContentLoaded', () => {
  document.documentElement.lang = currentLang;
  document.documentElement.dir = currentLang === 'ar' ? 'rtl' : 'ltr';
  applyTranslations();
  document.querySelectorAll('.lang-btn').forEach(b =>
    b.classList.toggle('active', b.dataset.lang === currentLang)
  );
});
