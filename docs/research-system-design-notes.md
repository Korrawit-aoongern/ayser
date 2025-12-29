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

### 1.2 UptimeRobot : Pros and Cons

### 1.3 Grafana : Pros and Cons

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

## 3. Frontend

## 4. Backend

## 5. Infra

## 6. Database
