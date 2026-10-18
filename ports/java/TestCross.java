import java.nio.file.*;
public class TestCross {
  public static void main(String[]a)throws Exception{
    byte[] b=Files.readAllBytes(Paths.get("/tmp/cross.json"));
    String j=new String(b);
    long[] arr=extract(j,"a"), exp=extract(j,"exp");
    long[] c=arr.clone(); NovaSuper.sort(c);
    boolean ok=true;
    for(int i=0;i<c.length;i++){ if(c[i]!=exp[i]){ok=false; System.out.println("bad"+i); break;}}
    if(ok) System.out.println("ok");
  }
  static long[] extract(String j,String k){
    int idx=j.indexOf("\""+k+"\""); int s=j.indexOf("[",idx); int e=j.indexOf("]",s);
    String[] p=j.substring(s+1,e).split(","); long[] r=new long[p.length];
    for(int i=0;i<p.length;i++) if(!p[i].trim().isEmpty()) r[i]=Long.parseLong(p[i].trim());
    return r;
  }
}
