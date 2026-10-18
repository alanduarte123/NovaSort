#include <stdio.h>
#include <stdlib.h>
#include <stdint.h>
#include <stdbool.h>
#include <string.h>
void nova_super(int64_t *a,int n);
int main(){
  FILE *f=fopen("/tmp/cross.json","r");
  if(!f) return 1;
  fseek(f,0,SEEK_END); long sz=ftell(f); rewind(f);
  char *buf=malloc(sz+1); fread(buf,1,sz,f); fclose(f); buf[sz]=0;
  // naive extract a
  char *p=strstr(buf,"\"a\"");
  p=strchr(p,'['); int depth=0; char *s=p; while(*s){if(*s=='[')depth++; if(*s==']'){depth--; if(depth==0){s++; break;}} s++;}
  int n=1; for(char *t=p+1;t<s-1;t++) if(*t==',') n++;
  int64_t *A=malloc(n*sizeof(int64_t)); char *tok=strtok(strndup(p+1,s-p-2),","); int i=0;
  while(tok){ A[i++]=atoll(tok); tok=strtok(NULL,","); }
  // exp extract small
  int64_t *B=malloc(n*sizeof(int64_t));
  char *pe=strstr(buf,"\"exp\""); pe=strchr(pe,'[');
  char *se=pe; depth=0; while(*se){if(*se=='[')depth++; if(*se==']'){depth--; if(depth==0){se++; break;}} se++;}
  tok=strtok(strndup(pe+1,se-pe-2),","); i=0; while(tok){ B[i++]=atoll(tok); tok=strtok(NULL,","); }
  int64_t *R=malloc(n*sizeof(int64_t)); for(int j=0;j<n;j++) R[j]=A[j];
  nova_super(R,n);
  bool ok=true; for(int j=0;j<n;j++) if(R[j]!=B[j]){ok=false; printf("bad %d\n",j); break;}
  if(ok) printf("ok\n");
  free(buf); free(A); free(B); free(R); return 0;
}
