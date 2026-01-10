# System Design Research Notes

## 1. Monitoring

### 1.1 Prometheus: Pros and Cons

Prometheus เป็นระบบ monitoring แบบ open-source ที่ได้รับความนิยมสูงในระบบ cloud-native และ Kubernetes อย่างไรก็ตาม Prometheus มีทั้งข้อดีและข้อจำกัด เมื่อพิจารณาในบริบทของผู้ใช้งานเป้าหมายของ Ayser

#### ข้อดี

- เป็น Open-Source และมี community ขนาดใหญ่
- รองรับการค้นพบ service และ automation ได้ดี
- ใช้โมเดลแบบ Pull-based ในการเก็บ metrics ผ่าน HTTP endpoint
- มีภาษา query (PromQL) ที่ทรงพลัง
- เหมาะสมกับสภาพแวดล้อมแบบ Kubernetes
- มี ecosystem ที่รองรับอย่างกว้างขวาง
- สามารถรองรับระบบขนาดใหญ่ได้ในระดับสูง

#### ข้อจำกัด

- โครงสร้างแบบ Single-node ทำให้การ scale และ deployment ที่ซับซ้อนทำได้ยาก
- ไม่ใช่ระบบ logging จำเป็นต้องใช้เครื่องมืออื่นร่วมด้วย
- ไม่เหมาะสำหรับการเก็บข้อมูลระยะยาว
- ไม่ได้ออกแบบมาเพื่อแสดงผลผ่าน dashboard โดยตรง
- ต้องใช้ exporter สำหรับหลายบริการที่ไม่รองรับโดยตรง
- มีข้อกังวลด้านความปลอดภัยจากการเปิด HTTP metrics endpoint
- ต้องอาศัยความรู้ทางเทคนิคระดับสูงในการติดตั้งและดูแลรักษา

จากการวิเคราะห์ พบว่า Prometheus มีความสามารถสูง แต่มีความซับซ้อนเกินความจำเป็นสำหรับผู้ใช้งานเป้าหมายของ Ayser

```
“ Ayser ไม่ได้มีเป้าหมายที่จะแทนที่ Prometheus แต่สามารถอ้างอิงการทำงานจาก Prometheus เท่านั้น ”
```

**แหล่งที่มา** : [Pros and Cons of Prometheus. In short, Prometheus is a monitoring… | by Doga Budak | Medium](https://medium.com/@dogabudak/pros-and-cons-of-prometheus-b04ab3afcbf7)

---
### 1.2 UptimeRobot : Pros and Cons

#### ข้อดีของ UptimeRobot
- ใช้งานง่ายและติดตั้งรวดเร็ว เหมาะทั้งผู้ใช้ทั่วไปและองค์กร
- การแจ้งเตือนแบบเรียลไทม์ ช่วยให้แก้ปัญหา downtime ได้ทันที
- อินเทอร์เฟซเป็นมิตรต่อผู้ใช้ ไม่ซับซ้อน ใช้งานสะดวก
- ความน่าเชื่อถือสูง ตรวจสอบ uptime ได้แม่นยำและสม่ำเสมอ
- การมอนิเตอร์ที่ปรับแต่งได้ ตั้งค่า alert ตามความต้องการ
- มีแผนฟรีที่คุ้มค่า ครอบคลุมฟีเจอร์พื้นฐานที่จำเป็น

#### ข้อเสียของ UptimeRobot
- การแจ้งเตือนบางครั้งล่าช้า ทำให้ตอบสนองต่อ downtime ไม่ทันเวลา
- ข้อจำกัดของแผนฟรี เช่น ความถี่ในการตรวจสอบและจำนวนเว็บไซต์ที่รองรับ
- ฟีเจอร์ขั้นสูงต้องจ่ายเพิ่ม เช่น การตรวจสอบภายในเครือข่ายหรือการตั้งค่าลึก
- ราคาสูง เมื่อเทียบกับคู่แข่ง โดยเฉพาะสำหรับผู้ใช้ในบางประเทศ
- การตั้งค่าซับซ้อน สำหรับผู้ที่ต้องการตรวจสอบเชิงลึก
- ความสับสนด้านราคาและการคิดเงิน ทำให้ผู้ใช้บางรายไม่พอใจ

#### สรุป
จากข้อดีและข้อจำกัดของ UptimeRobot ทำให้เห็นว่า
- ระบบ monitoring ที่ใช้งานง่ายและ setup ต่ำ มีคุณค่าสูงสำหรับผู้เริ่มต้น
- Blackbox monitoring เพียงอย่างเดียวไม่เพียงพอสำหรับการเข้าใจสุขภาพระบบเชิงลึก
- การแจ้งเตือนแบบ real-time มีประโยชน์ แต่เพิ่มความซับซ้อนของระบบ

ดังนั้น Ayser เลือกโฟกัสที่
- ความชัดเจนของสถานะระบบมากกว่าความถี่ของ alert
- การอธิบายสุขภาพระบบในระดับที่เข้าใจง่าย แทนการแจ้งเตือนจำนวนมาก

**แหล่งที่มา** : [UptimeRobot Pros and Cons: Top Advantages and Disadvantages](https://www.g2.com/products/uptimerobot/reviews?qs=pros-and-cons)

**แหล่งที่มา** : [Uptimerobot Reviews](https://www.softwareadvice.com/website-monitoring/uptimerobot-profile/reviews/)


---
### 1.3 Grafana : Pros and Cons

#### จุดเด่นของ Grafana
- การแสดงผลข้อมูลที่หลากหลาย รองรับกราฟ แผนภูมิ ตาราง heatmap และแผนที่ ทำให้เข้าใจข้อมูลง่ายขึ้น
- รวมข้อมูลจากหลายระบบได้ในแดชบอร์ดเดียว เช่น Prometheus, Loki, Mimir, Postgres, Cloudwatch metrics
- แดชบอร์ดปรับแต่งได้ ใช้งาน drag-and-drop และ template variables เพื่อสร้างแดชบอร์ดที่ยืดหยุ่น
- ระบบแจ้งเตือน ส่งผ่าน email, Slack, PagerDuty ฯลฯ เพื่อช่วยจัดการเหตุการณ์ได้ทันที
- ชุมชนและ ecosystem แข็งแกร่ง มีปลั๊กอินและแดชบอร์ดที่พัฒนาโดยผู้ใช้จำนวนมาก
- การแชร์และการเข้าถึงง่าย สามารถแบ่งปันแดชบอร์ดให้ทีมงานหรือสาธารณะได้
- ฟีเจอร์ด้านความปลอดภัย รองรับ MFA และการจัดการสิทธิ์ผู้ใช้
- รองรับการขยายตัว (Scalability) ใช้งานได้ตั้งแต่ระบบเล็กไปจนถึงองค์กรใหญ่
- คุ้มค่าและประหยัดต้นทุน เป็น open-source และมีแผนฟรีตลอดชีพ
- สามารถขยายเป็น LGTM Stack (Loki, Grafana, Tempo, Mimir) เพื่อรองรับ Logs, Metrics และ Traces ได้ครบ

#### ข้อจำกัดของ Grafana
- ไม่ใช่ระบบเก็บข้อมูลเอง ต้องพึ่งพาเครื่องมืออื่น เช่น Prometheus, Loki, Jaeger
- ความซับซ้อนและเส้นทางการเรียนรู้สูง ต้องใช้เวลาและทักษะทางเทคนิคในการตั้งค่าและปรับแต่ง
- ปัญหาการเชื่อมต่อกับฐานข้อมูลบางประเภท โดยเฉพาะที่ไม่มีปลั๊กอินรองรับ
- การใช้ทรัพยากรสูง เมื่อโหลดแดชบอร์ดที่ซับซ้อนหรือ query จำนวนมาก
- ข้อจำกัดของระบบแจ้งเตือน ยังไม่เทียบเท่าเครื่องมือเฉพาะด้าน incident management
- การจัดการสิทธิ์เข้าถึงยุ่งยาก โดยเฉพาะในองค์กรขนาดใหญ่
- ข้อจำกัดด้านการแสดงผลและ UI ต้องพึ่งพาปลั๊กอินหรือการพัฒนาเพิ่มเติม
- การสนับสนุนจากชุมชนไม่สม่ำเสมอ และการสนับสนุนอย่างเป็นทางการมีเฉพาะในแผน Enterprise
- การทำรายงานแบบ static ยาก เช่น PDF หรือ email report ต้องใช้ปลั๊กอินเสริม
- พึ่งพาแหล่งข้อมูลภายนอก หากแหล่งข้อมูลมีปัญหา Grafana ก็จะได้รับผลกระทบโดยตรง
- ไม่เหมาะหากใช้เพียงตัวเดียว เพราะ Grafana เพียงอย่างเดียวไม่สามารถทำ Logging, Metrics และ Tracing ได้ครบ

#### สรุป
Grafana แสดงให้เห็นว่า
- Visualization ที่ทรงพลังช่วยให้เข้าใจข้อมูลได้ดี แต่แลกกับความซับซ้อนสูง
- การพึ่งพา ecosystem หลายตัวทำให้ learning curve สูง
- ผู้ใช้ต้องมีความรู้ด้าน metrics และ query ในระดับหนึ่ง

Ayser จึงตั้งใจไม่แข่งขันกับ Grafana ในด้าน visualization
แต่เลือกเป็น monitoring layer ที่
- สรุปสถานะระบบให้เข้าใจง่าย
- ลดภาระการตีความ metrics สำหรับผู้ใช้
- ทำหน้าที่เป็น “health interpreter” มากกว่า “data explorer”

**แหล่งที่มา** : [Maximize the Potential: A Deep Dive into Grafana Pros and Cons](https://edgedelta.com/company/blog/grafana-pros-and-cons)

**แหล่งที่มา** : [Open Source Monitoring tools : SigNoz Vs Grafana Vs The Elastic Stack](https://www.reddit.com/r/devops/comments/1b0e745/open_source_monitoring_tools_signoz_vs_grafana_vs/)

---
### 1.4 Blackbox Monitoring (URL-based)

### 1.5 Gray-box Monitoring (URL + /metrics endpoint)

### 1.6 Cloud Provider Monitoring (URL + OAuth)

### 1.7 Custom Provider / Advance user (URL + Custom API key Structure based on Cloud Provider)

### 1.8 Monitoring Input Methods Consideration

Ayser รองรับวิธีการป้อนข้อมูลการตรวจสอบหลายวิธี โดยมีข้อแลกเปลี่ยนที่แตกต่างกันระหว่างความเรียบง่าย ความลึกของข้อมูลเชิงลึก และความรับผิดชอบด้านความปลอดภัย

ระบบให้ความสำคัญกับ:

1. การติดตั้งน้อยที่สุดสำหรับผู้ใช้ที่ไม่เชี่ยวชาญด้านเทคนิค
2. การจัดการข้อมูลประจำตัวอย่างปลอดภัย
3. ความซับซ้อนที่เพิ่มขึ้นสำหรับผู้ใช้ขั้นสูง

จากข้อมูลนี้ Ayser จึงนำรูปแบบการป้อนข้อมูลแบบหลายระดับมาใช้:
- การตรวจสอบแบบกล่องดำตาม URL เป็นค่าเริ่มต้น
- URL + /metrics endpoint สำหรับผู้ใช้ที่เป็นนักพัฒนา
- การผสานรวมระบบคลาวด์แบบ OAuth สำหรับการใช้งานขั้นสูงที่ปลอดภัย
- การผสานรวมแบบกำหนดเองสำหรับผู้ใช้ขั้นสูงเท่านั้น

## 2. ML Service

### How Machine Learning helps a Monitoring Platform? (Stub ; To be Research)

ในระบบ monitoring แบบดั้งเดิม ผู้ใช้งานมักต้องตีความข้อมูลจาก metric จำนวนมาก
เช่น latency, error rate, CPU, memory และ network usage
ซึ่งต้องอาศัยความรู้เชิงเทคนิคและประสบการณ์ในการตัดสินใจ

ใน Ayser, Machine Learning ไม่ได้ถูกนำมาใช้เพื่อการวิเคราะห์เชิงลึก (analytics)
แต่ทำหน้าที่เป็นตัวช่วย “ตีความ” สัญญาณสุขภาพของระบบ
เพื่อสรุปสถานะให้อยู่ในรูปแบบที่ผู้ใช้งานเข้าใจได้ง่าย

บทบาทหลักของ ML ใน Ayser ได้แก่:
- การสรุปสถานะสุขภาพของระบบจาก metric หลายตัว
- การเรียนรู้ baseline การทำงานปกติของแต่ละ service
- การระบุความผิดปกติในระดับเบื้องต้น
- การให้คำแนะนำเชิงนุ่มนวล (soft suggestion) เกี่ยวกับสาเหตุที่เป็นไปได้

ML Service ใน Ayser ถูกออกแบบให้เป็น decision-support layer
เพื่อช่วยให้ผู้ใช้งานเข้าใจสถานะของระบบได้เร็วขึ้น
โดยไม่มุ่งเน้นการวิเคราะห์เชิงธุรกิจหรือการคาดการณ์ระยะยาว

รายละเอียดเชิงลึกเกี่ยวกับโมเดลและเทคนิคจะถูกศึกษาเพิ่มเติมในภายหลัง

---
### Why Ayser Uses Machine Learning?

Ayser ถูกออกแบบมาเพื่อเป็น Website & Service Health Advisor
ไม่ใช่ analytics platform หรือ business intelligence system

เป้าหมายหลักของระบบคือ
การช่วยให้ผู้ใช้งานเข้าใจว่า “ขณะนี้ระบบอยู่ในสภาพใด”
และ “ควรกังวลหรือไม่” โดยไม่ต้องตีความ metric จำนวนมากด้วยตนเอง

Machine Learning ถูกนำมาใช้ใน Ayser ด้วยเหตุผลดังนี้:

### 1. ลดภาระการตีความข้อมูลของผู้ใช้งาน

ผู้ใช้งานจำนวนมากไม่ใช่ผู้เชี่ยวชาญด้าน DevOps
การแสดง metric ดิบจำนวนมากอาจทำให้เกิดความสับสนมากกว่าประโยชน์

ML ช่วยแปลงข้อมูลหลายตัว
ให้กลายเป็นสถานะสุขภาพระดับสูง เช่น
- Normal
- Warning
- Degraded
- Critical

### 2. รองรับ baseline ของระบบที่แตกต่างกัน

แต่ละ service มีพฤติกรรม “ปกติ” ที่ไม่เหมือนกัน
การใช้ threshold แบบตายตัวอาจทำให้เกิด false alert

ML ช่วยเรียนรู้ baseline ของแต่ละระบบ
และใช้ baseline นั้นในการประเมินความผิดปกติ
แทนการใช้ค่าคงที่เดียวกับทุก service

### 3. ช่วยระบุความผิดปกติแบบเรียบง่าย

ML ใน Ayser ไม่ได้มุ่งเน้น anomaly detection ขั้นสูง
แต่เน้นการระบุความผิดปกติในระดับที่เข้าใจง่าย
เพื่อเป็นสัญญาณเตือนให้ผู้ใช้งานตรวจสอบต่อ

### 4. ให้คำแนะนำเชิงสนับสนุน (Advisory)

ML สามารถช่วยเชื่อมโยงสัญญาณพื้นฐาน เช่น
- latency สูงร่วมกับ CPU สูง
- error rate เพิ่มขึ้นโดย latency คงที่

เพื่อให้คำแนะนำเชิงนุ่มนวลเกี่ยวกับสาเหตุที่เป็นไปได้
โดยไม่ตัดสินหรือดำเนินการแทนผู้ใช้งาน

### สิ่งที่ Ayser ตั้งใจไม่ใช้ Machine Learning ทำ

เพื่อควบคุมขอบเขตของระบบและลดความซับซ้อน
Ayser จะไม่ใช้ ML สำหรับ:
- การวิเคราะห์แนวโน้มระยะยาว
- การวางแผน capacity
- การวิเคราะห์พฤติกรรมผู้ใช้งาน
- การตัดสินใจหรือแก้ไขระบบโดยอัตโนมัติ

การตัดสินใจใช้ Machine Learning ใน Ayser
เป็นการใช้ ML ในบทบาทของ “ผู้ช่วยแปลสัญญาณ”
ไม่ใช่ระบบวิเคราะห์หรือควบคุมระบบแทนมนุษย์

## 3. Frontend

### 1. Best Possible Frontend Framework for Monitoring Platform App (Focus on Speed)
### Svelte
- เปลี่ยนกระบวนการส่วนใหญ่ไปทำที่ขั้นตอนการคอมไพล์ ทำให้ได้โค้ด JavaScript บริสุทธิ์ที่ได้รับการปรับแต่งมาอย่างดี โดยมีค่าใช้จ่ายในการทำงาน (runtime overhead) น้อยที่สุด นำไปสู่ประสิทธิภาพที่รวดเร็วเป็นพิเศษและขนาดบันเดิล (bundle size) ที่เล็ก นี่เป็นตัวเลือกที่เหมาะอย่างยิ่งสำหรับแอปพลิเคชันที่ต้องการอัปเดต UI อย่างรวดเร็วและมีความหน่วงต่ำสุด (minimal latency)

### SolidJS
- มอบประสิทธิภาพที่ยอดเยี่ยมผ่านระบบรีแอกทิวิตี้ (reactivity system) แบบละเอียด (fine-grained) ซึ่งจะอัปเดตเฉพาะส่วนที่จำเป็นของ DOM โดยไม่ต้องใช้ Virtual DOM (VDOM) มันมอบประสบการณ์การพัฒนาที่คล้ายคลึงกับ React แต่ทำคะแนนได้สูงกว่าอย่างสม่ำเสมอในการทดสอบเปรียบเทียบประสิทธิภาพ (performance benchmarks)

### จากการเปรียบเทียบพบว่า:
- Svelte เหมาะกับระบบที่ต้องการ performance สูงและโค้ดเรียบง่าย
- SolidJS ให้ประสิทธิภาพที่ดีมาก แต่ยังมี ecosystem และ tooling ที่เล็กกว่า

สำหรับ Ayser ซึ่งเป็นโปรเจคเพื่อการเรียนรู้ system design และ monitoring concept

**Svelte** มีความเหมาะสมมากกว่าในด้าน:
- ความง่ายในการพัฒนาและดูแลรักษา
- ความชัดเจนของโค้ด
- การลดความซับซ้อนที่ไม่จำเป็นของ frontend

ทั้งนี้ การเลือก framework ใน Ayser มีเป้าหมายเพื่อ
สนับสนุนความเข้าใจของระบบ monitoring
มากกว่าการแข่งขันด้าน feature หรือ framework popularity

**แหล่งที่มา** : [Choosing the Best JavaScript Framework in 2026: A Complete Guide for Enterprise and Modern Web Development](https://www.sencha.com/blog/how-to-choose-the-best-javascript-frameworks-in-2023/)

**แหล่งที่มา** : [I built an app in every frontend framework](https://dev.to/lissy93/i-built-an-app-in-every-frontend-framework-4a9g)

---
### 2. Why SvelteKit for Ayser

สืบเนื่องจาก Svelte ที่เหมาะสม...
SvelteKit ถูกเลือกเป็น application framework สำหรับ Ayser
เนื่องจาก Ayser เป็น web application ที่ต้องการมากกว่าเพียงการแสดงผล UI

SvelteKit ให้โครงสร้างที่เหมาะสมสำหรับ:
- Routing และ layout ที่เป็นระบบ
- การโหลดข้อมูลจาก backend อย่างเป็นระเบียบ
- การแยก client-side และ server-side logic อย่างชัดเจน

#### 1. Built-in Routing and Layout

SvelteKit มีระบบ routing และ layout มาให้ในตัว
ช่วยลด boilerplate และทำให้โครงสร้างโปรเจคชัดเจน

เหมาะกับ monitoring dashboard
ที่ต้องมีหลายหน้า เช่น:
- Service list
- Service detail
- Health overview
- Configuration page

#### 2. Server-side Data Loading

SvelteKit รองรับการโหลดข้อมูลจาก server ผ่าน `load` function
ช่วยให้สามารถ:
- ดึงข้อมูล metrics ก่อน render หน้า
- ควบคุมการเรียก API ได้อย่างเป็นระบบ
- ลด logic ซ้ำซ้อนใน frontend

สิ่งนี้เหมาะกับระบบ monitoring
ที่ต้องแสดงข้อมูลสถานะทันทีเมื่อเปิดหน้า

#### 3. SSR and Performance Consideration

แม้ Ayser จะไม่เน้น SEO
แต่การรองรับ Server-Side Rendering (SSR)
ช่วยให้หน้า dashboard แสดงผลได้รวดเร็ว
โดยเฉพาะในกรณีที่ต้องโหลดข้อมูลสถานะเริ่มต้นจำนวนมาก


#### 4. Unified Frontend and Backend Entry Point

SvelteKit ช่วยรวม frontend และ server logic ไว้ในโปรเจคเดียว
เช่น:
- API routes
- Authentication logic
- Proxy calls ไปยัง backend service

เหมาะกับ Ayser ในฐานะระบบทดลองด้าน system design
ที่ต้องการเห็นภาพ end-to-end flow ชัดเจน


#### 5. Minimal Runtime Overhead

SvelteKit ยังคงคุณสมบัติหลักของ Svelte:
- Runtime overhead ต่ำ
- Bundle size เล็ก
- UI ตอบสนองเร็ว

ซึ่งสอดคล้องกับเป้าหมายของ Ayser
ที่เน้นความเร็วและความเรียบง่าย

การเลือก SvelteKit ใน Ayser
มีเป้าหมายเพื่อสร้างโครงสร้างแอปพลิเคชันที่ชัดเจน
เข้าใจง่าย และเหมาะกับการศึกษาแนวคิดของ monitoring platform

**แหล่งที่มา** : [Introduction SvelteKit Docs](https://svelte.dev/docs/kit/introduction)

**แหล่งที่มา** : [Beginner's Guide to Svelte and SvelteKit](https://prismic.io/blog/svelte-and-sveltekit)

---
### 3. Design Consideration for Ayser Frontend

Ayser เป็น monitoring platform ที่เน้น:
- ความเร็วในการแสดงผลสถานะระบบ
- UI ที่เรียบง่ายและเข้าใจทันที
- การอัปเดตข้อมูลเป็นระยะ (near real-time) แต่ไม่ต้องเป็น realtime dashboard เต็มรูปแบบ

ดังนั้น frontend framework ที่เหมาะสมควรมีคุณสมบัติดังนี้:
- Runtime overhead ต่ำ เพื่อให้ UI ตอบสนองเร็ว
- State management เรียบง่าย ไม่ซับซ้อน
- Bundle size เล็ก เพื่อลดเวลาโหลดหน้าเว็บ
- ไม่จำเป็นต้องพึ่งพา ecosystem ขนาดใหญ่


## 4. Backend

## 5. Infra

## 6. Database
