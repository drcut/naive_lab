#include <iostream>
#include <fstream>
#include <cstdio>
#include <cstdlib>
#include <map>
#include <cstring>
#include <string>
using namespace std;
int main()
{
	ifstream fin_vec;
	fin_vec.open("vector.txt",ios::in);
	char* tmp = new char[3400];
	float* tmp_vec;
	map<string,float*>dic;
	map<string,float*>::iterator it; 
	/*fin_vec.getline(tmp,3400);//pass the first line
	
	
	int have=0;
	while(fin_vec>>tmp)
	{ 
		tmp_vec = new float[200];
		//printf("%s\n",tmp);
		for(int i = 0;i<200;i++)
		{
			fin_vec>>tmp_vec[i];
		}
		dic.insert(pair<string,float*>(tmp,tmp_vec));
	}*/
	fin_vec.close();
	fin_vec.open("sift_lines.txt",ios::in);
	ofstream fout;
	fout.open("vec_result.txt",ios::out);
	while(fin_vec>>tmp)
	{
		cout<<tmp;
		getchar();
		if(tmp[0]=='E'){fout<<endl;continue;}

		it=dic.find(tmp);
		if(it!=dic.end())
		{
			for(int i = 0;i<200;i++)
				fout<<it->second[i]<<' ';
			fout<<endl;
			//getchar();
		}
	}
	fin_vec.close();
	fout.close();
	/*fout.close();
	ofstream fout1;
	fout1.open("dic.txt",ios::out);
	for(it=dic.begin();it!=dic.end();it++)
		fout1<<it->first<<' '<<it->second<<endl;
	fout1.close();*/
	return 0;
}
