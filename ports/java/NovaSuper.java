import java.io.*;
import java.util.*;

public class NovaSuper {
  public static void sort(long[] a){
    int n = a.length;
    if(n<=1) return;
    if(n<32){
      for(int i=1;i<n;i++){
        long v=a[i]; int j=i-1;
        while(j>=0 && a[j]>v){ a[j+1]=a[j]; j--; }
        a[j+1]=v;
      }
      return;
    }
    long minv=a[0], maxv=a[0];
    for(int i=1;i<n;i++){ if(a[i]<minv) minv=a[i]; if(a[i]>maxv) maxv=a[i]; }
    long r=maxv-minv+1;
    int limitCount = 65536; if(n>limitCount) limitCount=n;
    if(r >=1 && r <= limitCount){
      int len = (int)r;
      int[] cnt = new int[len];
      for(int i=0;i<n;i++) cnt[(int)(a[i]-minv)]++;
      int k=0;
      for(int i=0;i<len;i++){
        long v=minv+i; int c=cnt[i];
        Arrays.fill(a,k,k+c,v); k+=c;
      }
      return;
    }
    long[] voff = new long[n];
    for(int i=0;i<n;i++) voff[i] = a[i]-minv;
    // low
    int[] d0 = new int[n];
    for(int i=0;i<n;i++) d0[i] = (int)(voff[i] & 0xFFFFL);
    int[] idx0 = argsortStable(d0);
    long[] v1 = new long[n];
    for(int i=0;i<n;i++) v1[i] = voff[idx0[i]];
    // high
    int[] d1 = new int[n];
    for(int i=0;i<n;i++) d1[i] = (int)((v1[i] >> 16) & 0xFFFFL);
    int[] idx1 = argsortStable(d1);
    for(int i=0;i<n;i++) a[i] = v1[idx1[i]] + minv;
  }
  static int[] argsortStable(int[] b){
    Integer[] idx=new Integer[b.length];
    for(int i=0;i<b.length;i++) idx[i]=i;
    Arrays.sort(idx,(i,j)->{ if(b[i]!=b[j]) return Integer.compare(b[i],b[j]); return Integer.compare(i,j); });
    int[] r=new int[b.length];
    for(int i=0;i<b.length;i++) r[i]=idx[i];
    return r;
  }
  public static void main(String[] args){
    long[] a={3,1,2,3,1};
    sort(a);
    System.out.print(a[0]+","+a[1]+","+a[2]+","+a[3]+","+a[4]);
  }
}
