# Ayser

Ayser คือระบบสำหรับตรวจสอบสถานะและสุขภาพของ service หรือเว็บไซต์
โดยมุ่งเน้นที่การแสดงผล สถานะการทำงาน (status) และ health ของ service เป็นหลัก

โปรเจคนี้ถูกสร้างขึ้นเพื่อศึกษาแนวคิดด้าน System Design, DevOps และ Observability
โดยเน้นความเข้าใจว่า ระบบ monitoring ทำงานอย่างไร มากกว่าการสร้าง dashboard ที่ซับซ้อน

## Ayser คืออะไร

Ayser เป็นแพลตฟอร์ม monitoring ที่สามารถเก็บข้อมูลพื้นฐานของ service ได้ เช่น

- สถานะการทำงาน (Up / Down)
- เวลาในการตอบสนอง (Latency)
- ตัวชี้วัดด้านสุขภาพของระบบ (Health metrics)

ระบบถูกออกแบบให้ยืดหยุ่นตามระดับข้อมูลที่ผู้ใช้งานสามารถให้ได้
ตั้งแต่การตรวจสอบ URL ธรรมดา ไปจนถึงการดึง metrics จาก endpoint หรือ cloud platform

## ทำไมถึงสร้าง Ayser

- ระบบ monitoring หลายตัวถูกใช้งานโดยไม่เข้าใจว่าข้อมูลมาจากไหน
- ผู้เริ่มต้นมักเห็นแต่กราฟ แต่ไม่เข้าใจกลไกเบื้องหลัง
- Ayser ถูกสร้างขึ้นเพื่อเรียนรู้ **“How monitoring systems actually work”**

เป้าหมายหลักคือความชัดเจนของแนวคิด ไม่ใช่ความซับซ้อนของฟีเจอร์

## ภาพรวมสถาปัตยกรรม (High-level)

Ayser แบ่งออกเป็นองค์ประกอบหลักดังนี้

- **Frontend**

    Dashboard สำหรับแสดงสถานะและข้อมูลสุขภาพของ service
- **Backend**

    API และ logic สำหรับจัดการข้อมูลและการตั้งค่า
- **Service Layer**

    ระบบเก็บ metrics (collector และ ML/analysis service)
- **Infrastructure / DevOps**

    การ deploy และ pipeline ด้วย GitLab CI/CD

## วิธีการเก็บ Metrics

Ayser รองรับการเก็บข้อมูลสุขภาพของ service หลายระดับ
เพื่อให้เหมาะกับผู้ใช้งานตั้งแต่ระดับเริ่มต้น ไปจนถึงผู้ใช้ขั้นสูง

แนวคิดหลักคือ
> **“ให้ข้อมูลเท่าที่ผู้ใช้สามารถให้ได้ โดยไม่บังคับความซับซ้อน”**

### 1. Blackbox Monitoring (URL-based)

เหมาะสำหรับผู้ใช้งานที่มีเพียง URL ของเว็บไซต์หรือ service
ไม่ต้องมีการตั้งค่าเพิ่มเติมในระบบปลายทาง

ข้อมูลที่สามารถเก็บได้:
- สถานะการทำงาน (Up / Down)
- HTTP status code
- เวลาในการตอบสนอง (Latency)
- การเข้าถึงได้ของหน้าเว็บหรือ API

ข้อดี:
- ตั้งค่าง่ายที่สุด
- ไม่ต้องมีความรู้ด้าน DevOps
- เหมาะสำหรับเว็บไซต์ทั่วไป

ข้อจำกัด:
- ไม่เห็นข้อมูลภายในของระบบ
- วิเคราะห์สาเหตุเชิงลึกไม่ได้

---

### 2. Gray-box Monitoring (URL + /metrics Endpoint)

ใช้เมื่อ service มี metrics endpoint เช่น `/metrics`
รองรับรูปแบบ Prometheus / OpenMetrics

ข้อมูลที่สามารถเก็บได้:
- CPU, Memory, Disk, Network
- Latency (p50, p90, p99)
- Error rate และ request count
- Application-specific metrics

ข้อดี:
- เห็นสุขภาพระบบในระดับลึกขึ้น
- ยังไม่ซับซ้อนเท่าระบบ enterprise
- เหมาะกับ service ที่พัฒนาเอง

ข้อจำกัด:
- ต้องมีการ expose metrics endpoint
- ต้องเข้าใจ metrics พื้นฐาน

---

### 3. Cloud Provider Monitoring (URL + OAuth)

ใช้ข้อมูลจาก Cloud Provider โดยตรงผ่าน OAuth หรือ API
เช่น AWS, GCP, Azure, Vercel

ข้อมูลที่สามารถเก็บได้:
- CPU / Memory utilization
- Network traffic
- Database และ load balancer metrics
- Health status จากระบบของผู้ให้บริการ

ข้อดี:
- ข้อมูลเชื่อถือได้จาก platform โดยตรง
- ไม่ต้องแก้ไข code ของ service
- เหมาะกับระบบที่รันบน cloud เต็มรูปแบบ

ข้อจำกัด:
- ผูกกับผู้ให้บริการรายนั้น
- มีข้อจำกัดด้าน permission และ quota

---

### 4. Custom Provider / Advanced User

สำหรับผู้ใช้งานขั้นสูงที่ต้องการเชื่อมต่อระบบเฉพาะทาง
โดยใช้ Custom API หรือ API key structure ของแต่ละ provider

แนวคิดคือ:
- ใช้รูปแบบการเก็บข้อมูลคล้าย Cloud Provider Monitoring
- รองรับ API key (โปรดระมัดระวัง) และ endpoint ที่แตกต่างกันตามแต่ละบริการ

ตัวอย่างการใช้งาน:
- Hosting provider ที่มี REST API ของตนเอง
- Platform ที่ให้ข้อมูล health หรือ usage ผ่าน API
- Third-party service ที่ต้องใช้ API key ในการเข้าถึงข้อมูล

ข้อดี:
- รองรับบริการได้หลากหลายมากขึ้น
- ไม่ผูกกับ cloud provider รายใดรายหนึ่ง
- ได้ข้อมูลสุขภาพระบบหลากหลายเหมือน Cloud Provider Monitoring

ข้อจำกัด:
- ต้องระมัดระวังเรื่องความปลอดภัยของ API key และ Secret
- ต้องมีความรู้เชิงเทคนิค
- ต้องจัดการ security และ data mapping เอง
- ไม่รองรับ metrics เชิงลึกหรือแบบ custom


## สถานะของโปรเจค

โปรเจคนี้อยู่ระหว่างการพัฒนา
- โฟกัสหลัก: การแสดงสถานะและสุขภาพของ service, Blackbox Monitoring, Gray-box Monitoring
- โฟกัสรอง: Cloud Provider Monitoring (URL + OAuth) และ Custom Provider / Advanced User
- ฟีเจอร์เสริม เช่น alert, notification และ realtime dashboard
เป็นแนวทางต่อยอดในอนาคต

## Tech Stack (เบื้องต้น)

- Frontend: TBD
- Backend: TBD
- CI/CD: GitLab CI
- Monitoring Concepts: Prometheus-style metrics, Blackbox monitoring, Gray-box Monitoring

## เอกสารเพิ่มเติม

เอกสารด้าน requirement, proposal และ research จะถูกเก็บไว้ในโฟลเดอร์

```
docs/
```

เพื่อแยกออกจากโค้ดและดูแลได้เป็นระบบ

## หมายเหตุ

Ayser ถูกพัฒนาขึ้นในฐานะโปรเจคเพื่อการเรียนรู้
โดยเน้นความเข้าใจเชิงแนวคิด มากกว่าการแข่งขันด้าน performance หรือ feature completeness