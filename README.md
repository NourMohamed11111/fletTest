# IoT Dashboard — نسخة موبايل

## اللي اتغيّر عن الكود الأصلي
1. **ربط الملفين ببعض**: فصلت الاتصال بـ Firebase في ملف `firebase_service.py` منفصل، و`main.py` بقى بس مسؤول عن الواجهة.
2. **استخدمت بيانات مشروعك الحقيقي** (`maker-day-18`) بدل الـ placeholder اللي كان في الكود.
3. **صلّحت أسماء الحقول** عشان تطابق الداتابيز الحقيقية اللي في السكرين شوت:
   - `commands/motor_dir` و `commands/motor_speed` (مش `commands/motor/dir` و `speed`)
   - `sensors/humidity`, `sensors/light_pct`, `sensors/temperature` (مفيش `light` أو `motion` جوه `sensors`)
   - `events/last_motion` (المضان اتنقل هنا مش تحت `sensors`)
   - في node اسمه `pump` مقفول في السكرين شوت — عرضته كـ raw data لحد ما تبعتلي شكل بياناته الحقيقي وأربطه صح.
   - `motor_speed` في قاعدة بياناتك بيتسجل كرقم من 0-255 (PWM)، فالسلايدر بيبعت نسبة 0-100% وبيتحول تلقائي.
4. **شكل موبايل حقيقي مش صفحة ويب طويلة**:
   - `AppBar` فوق زي أي تطبيق موبايل
   - `NavigationBar` تحت بتنقّل بين شاشتين: Dashboard و Control (بدل ما كل حاجة تبقى في عمود طويل واحد)
   - `page.adaptive = True` عشان الكنترولز تطلع بشكل Material على أندرويد وCupertino على iOS تلقائي
   - `SafeArea` عشان المحتوى ميدخلش تحت الـ notch أو status bar

## التشغيل والاختبار على الديسكتوب
```bash
pip install -r requirements.txt
python main.py
```

## بناء تطبيق أندرويد (APK)
```bash
flet build apk
```
هيطلعلك الملف في `build/apk/app-release.apk` وتقدر تنزّله على أي جهاز أندرويد مباشرة.

## قبل ما تشغّله
- الـ `pump` node لسه مش واضح شكله — ابعتلي سكرين شوت وهو مفتوح (مش مطوي) وأضيفلك كنترول حقيقي ليه.
- لو الـ ESP32 بتاعك بيقرأ `motor_speed` كنسبة مئوية مش PWM، قولي وأشيل التحويل من `firebase_service.py`.
