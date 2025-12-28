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
Ayser รองรับการเก็บข้อมูลได้หลายรูปแบบ ขึ้นอยู่กับการตั้งค่าของผู้ใช้

### 1. URL + Metrics Endpoint (Prometheus / OpenMetrics)
ใช้เมื่อ service มี endpoint สำหรับ metrics โดยเฉพาะ
สามารถเก็บข้อมูลได้ เช่น

- CPU, Memory, Disk, Network
- Latency (p50, p90, p99)
- Error rate และ request count
- Application-specific metrics

### 2. URL อย่างเดียว (Blackbox Monitoring)
ใช้เมื่อไม่มี metrics endpoint
ข้อมูลที่เก็บได้จะเป็นข้อมูลพื้นฐาน เช่น

- สถานะ Up / Down
- HTTP status code
- เวลาในการตอบสนองของหน้าเว็บ

### 3. Platform API (Cloud Provider)
ใช้ API key ของแพลตฟอร์ม เช่น AWS, Vercel หรือ Azure
สามารถเก็บข้อมูลระดับ infrastructure เช่น

- CPU / Memory utilization
- Network traffic
- Database และ load balancer metrics
- Health status จากระบบของผู้ให้บริการ

## สถานะของโปรเจค

โปรเจคนี้อยู่ระหว่างการพัฒนา
- โฟกัสหลัก: การแสดงสถานะและสุขภาพของ service
- ฟีเจอร์เสริม เช่น alert, notification และ realtime dashboard
เป็นแนวทางต่อยอดในอนาคต

## Tech Stack (เบื้องต้น)

- Frontend: TBD
- Backend: TBD
- CI/CD: GitLab CI
- Monitoring Concepts: Prometheus-style metrics, Blackbox monitoring

## เอกสารเพิ่มเติม

เอกสารด้าน requirement, proposal และ research จะถูกเก็บไว้ในโฟลเดอร์

```
docs/
```

เพื่อแยกออกจากโค้ดและดูแลได้เป็นระบบ

## หมายเหตุ

Ayser ถูกพัฒนาขึ้นในฐานะโปรเจคเพื่อการเรียนรู้
โดยเน้นความเข้าใจเชิงแนวคิด มากกว่าการแข่งขันด้าน performance หรือ feature completeness