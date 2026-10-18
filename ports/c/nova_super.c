#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <string.h>
#include <stdbool.h>
#include <limits.h>

typedef int64_t i64;

static void insertion_small(i64 *a, int n){
  for(int i=1;i<n;i++){
    i64 v=a[i]; int j=i-1;
    while(j>=0 && a[j]>v){ a[j+1]=a[j]; j--; }
    a[j+1]=v;
  }
}

static void stable_argsort16(i64 *keys, int n, int *idx){
  for(int i=0;i<n;i++) idx[i]=i;
  for(int gap=1;gap<n;gap<<=1){
    for(int i=gap;i<n;i++){
      int j=i-gap;
      int tmp=idx[i];
      while(j>=0 && keys[idx[j]]>keys[tmp]){
        idx[j+gap]=idx[j]; j-=gap;
      }
      idx[j+gap]=tmp;
    }
  }
}

void nova_super(i64 *a, int n){
  if(n<=1) return;
  if(n<32){ insertion_small(a,n); return; }
  i64 minv=a[0], maxv=a[0];
  for(int i=1;i<n;i++){ if(a[i]<minv) minv=a[i]; if(a[i]>maxv) maxv=a[i]; }
  i64 r = maxv - minv + 1;
  int limitCount = 65536;
  if(n > limitCount) limitCount = n;
  if(r >=1 && r <= limitCount){
    int len = (int)r;
    int *cnt = calloc(len, sizeof(int));
    if(cnt){
      for(int i=0;i<n;i++) cnt[a[i]-minv]++;
      int k=0;
      for(int i=0;i<len;i++){
        i64 v=minv+i;
        int c=cnt[i];
        for(int j=0;j<c;j++) a[k++] = v;
      }
      free(cnt); return;
    }
  }
  i64 *voff = malloc(n*sizeof(i64));
  for(int i=0;i<n;i++) voff[i] = a[i]-minv;
  int *d0 = malloc(n*sizeof(int));
  for(int i=0;i<n;i++) d0[i] = (int)(voff[i] & 0xFFFF);
  int *idx0 = malloc(n*sizeof(int));
  stable_argsort16((i64*)d0,n,idx0); // not quite keys type
  i64 *v1 = malloc(n*sizeof(i64));
  // better use int keys array
  free(d0);
  d0 = malloc(n*sizeof(int));
  for(int i=0;i<n;i++) d0[i]=(int)(voff[i]&0xFFFF);
  for(int i=0;i<n;i++) idx0[i]=i;
  // shell sort by key
  for(int gap=1;gap<n;gap<<=1){
    for(int i=gap;i<n;i++){
      int j=i-gap; int tmp=idx0[i];
      while(j>=0 && d0[idx0[j]]>d0[tmp]){ idx0[j+gap]=idx0[j]; j-=gap; }
      idx0[j+gap]=tmp;
    }
  }
  for(int i=0;i<n;i++) v1[i]=voff[idx0[i]];
  // high
  int *d1 = malloc(n*sizeof(int));
  for(int i=0;i<n;i++) d1[i]=(int)((v1[i]>>16)&0xFFFF);
  int *idx1 = malloc(n*sizeof(int));
  for(int i=0;i<n;i++) idx1[i]=i;
  for(int gap=1;gap<n;gap<<=1){
    for(int i=gap;i<n;i++){
      int j=i-gap; int tmp=idx1[i];
      while(j>=0 && d1[idx1[j]]>d1[tmp]){ idx1[j+gap]=idx1[j]; j-=gap; }
      idx1[j+gap]=tmp;
    }
  }
  i64 *out = malloc(n*sizeof(i64));
  for(int i=0;i<n;i++) out[i]=v1[idx1[i]]+minv;
  for(int i=0;i<n;i++) a[i]=out[i];
  free(voff); free(d0); free(idx0); free(v1); free(d1); free(idx1); free(out);
}
