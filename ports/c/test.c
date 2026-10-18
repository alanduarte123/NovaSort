#include <stdio.h>
#include <stdint.h>
void nova_super(int64_t *a,int n);
int main(){
  int64_t a[]={3,1,2,3,1};
  nova_super(a,5);
  for(int i=0;i<5;i++) printf("%lld%s",a[i],i<4?",":"");
  printf("\n");
  return 0;
}
