"""
اختبار الاتصال بقاعدة البيانات MySQL
"""
import mysql.connector
from config import Config

def test_connection():
    """اختبار الاتصال بقاعدة البيانات"""
    print("=" * 60)
    print("🔍 اختبار الاتصال بقاعدة البيانات MySQL")
    print("=" * 60)
    
    # عرض الإعدادات (بدون كلمة المرور)
    print("\n📋 إعدادات الاتصال:")
    print(f"   Host: {Config.mysql_config['host']}")
    print(f"   User: {Config.mysql_config['user']}")
    print(f"   Database: {Config.mysql_config['database']}")
    print(f"   Port: {Config.mysql_config['port']}")
    print(f"   Password: {'*' * len(Config.mysql_config['password'])}")
    
    try:
        # محاولة الاتصال
        print("\n🔌 جاري الاتصال...")
        conn = mysql.connector.connect(**Config.mysql_config)
        
        if conn.is_connected():
            print("✅ تم الاتصال بنجاح!")
            
            # الحصول على معلومات الخادم
            cursor = conn.cursor()
            cursor.execute("SELECT VERSION()")
            version = cursor.fetchone()
            print(f"   إصدار MySQL: {version[0]}")
            
            # عرض الجداول المتاحة
            print("\n📊 الجداول المتاحة في قاعدة البيانات:")
            cursor.execute("SHOW TABLES")
            tables = cursor.fetchall()
            
            if tables:
                for i, table in enumerate(tables, 1):
                    print(f"   {i}. {table[0]}")
            else:
                print("   ⚠️ لا توجد جداول في قاعدة البيانات")
            
            # اختبار جدول eduapi_lessoncontent
            print("\n🔍 فحص جدول eduapi_lessoncontent:")
            try:
                cursor.execute("SELECT COUNT(*) FROM eduapi_lessoncontent")
                count = cursor.fetchone()[0]
                print(f"   ✅ عدد السجلات: {count}")
                
                # عرض عينة من البيانات
                if count > 0:
                    cursor.execute("""
                        SELECT id, title, content_type 
                        FROM eduapi_lessoncontent 
                        LIMIT 5
                    """)
                    print("\n   📝 عينة من البيانات:")
                    for row in cursor.fetchall():
                        print(f"      ID: {row[0]}, Title: {row[1]}, Type: {row[2]}")
                        
            except mysql.connector.Error as e:
                print(f"   ⚠️ خطأ في الوصول للجدول: {e}")
            
            # اختبار جدول eduapi_lesson
            print("\n🔍 فحص جدول eduapi_lesson:")
            try:
                cursor.execute("SELECT COUNT(*) FROM eduapi_lesson")
                count = cursor.fetchone()[0]
                print(f"   ✅ عدد الدروس: {count}")
                
                if count > 0:
                    cursor.execute("""
                        SELECT id, name, subject, level 
                        FROM eduapi_lesson 
                        LIMIT 5
                    """)
                    print("\n   📚 عينة من الدروس:")
                    for row in cursor.fetchall():
                        print(f"      ID: {row[0]}, Name: {row[1]}, Subject: {row[2]}, Level: {row[3]}")
                        
            except mysql.connector.Error as e:
                print(f"   ⚠️ خطأ في الوصول للجدول: {e}")
            
            # إغلاق الاتصال
            cursor.close()
            conn.close()
            print("\n✅ تم إغلاق الاتصال بنجاح")
            
    except mysql.connector.Error as e:
        print(f"\n❌ فشل الاتصال!")
        print(f"   الخطأ: {e}")
        print("\n💡 تأكد من:")
        print("   1. تشغيل خادم MySQL")
        print("   2. صحة اسم المستخدم وكلمة المرور")
        print("   3. وجود قاعدة البيانات edu_system")
        print("   4. صلاحيات المستخدم للوصول لقاعدة البيانات")
        return False
    
    print("\n" + "=" * 60)
    return True

if __name__ == "__main__":
    test_connection()
