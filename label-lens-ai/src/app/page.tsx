'use client';

import React from "react";
import Layout from "@/app/components/Layout";
import {Button} from "@/app/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle} from "@/app/components/ui/card";
import { Alert, AlertDescription, AlertTitle } from "@/app/components/ui/alert";
import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  WarningCircleIcon,
  SecurityCameraIcon,
  CheckFatIcon,
  XIcon,
  FileLockIcon,
  FileTextIcon,
} from "@phosphor-icons/react";
import { Shield } from "lucide-react";

const Home =() => {
   
  //Mock Data
  const complianceScore = 72;
  const totalIssues = 8;
  const criticalIssues = 2;
  const highIssues = 2;
  const mediumIssues = 2;
  const lowIssues = 2;
  const resolvedIssues = 2;

  const recentIssues = [
    {
      id: '1',
      title: 'Missing FDA Required Disclaimer',
      severity: 'high',
      category: 'FDA Compliance',
      date: '2024-01-15',
      product: 'Vitamin C Serum'
    },
    {
      id: '2',
      title: 'Unsubstantiated Marketing Claims',
      severity: 'medium',
      category: 'FTC Compliance',
      date: '2024-01-14',
      product: 'Energy Bar'
    },
    {
      id: '3',
      title: 'Ingredient List Format Issue',
      severity: 'low',
      category: 'Labeling Standards',
      date: '2024-01-12',
      product: 'Organic Shampoo'
    }
  ];

  const getScoreColor = (score:number) => {
    if(score === 100) {
      return 'text-green-600';
    }
    if(score < 100 && score >= 60){
      return 'text-yellow-600';
    }

    return 'text-red-600';
  };

  const getBgColor = (score:number) => {
    if(score === 100) {
      return 'bg-green-50 border-green-600';
    }
    if(score < 100 && score >= 60){
      return 'bg-yellow-50 border-yellow-600';
    }

    return 'bg-red-50 border-red-600';
  };

  const getSeverityColor = (severity: string) => {
    if (severity === 'high'){
      return 'bg-red-100 text-red-600 border-red-200';
    } else if (severity === 'medium'){
      return 'bg-yellow-100 text-yellow-600 border-yellow-200';
    } else if (severity === 'low'){
      return 'bg-green-100 text-green-600 border-green-200';
    } else{
      return 'bg-gray-100 text-gray-600 border-gray-200';
    }
  };

  return (
    <Layout>
      <div className="max-w-7xl mx-auto space-y-8">
        <div className="flex justify-between items-start">
          <div>
            <h1 className="text-3xl font-bold text-slate-900 mb-2">Compliance Dashboard</h1>
            <p className="text-lg text-slate-600">Monitor you Compliance with your all inclusive Dashboard</p>
          </div>
          <Button className="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 mt-4 rounded-lg">New Analysis</Button>
        </div>

        <Card className={`${getBgColor(complianceScore)} border-2`}>
          <CardHeader className="pb-3">
            <CardTitle className="flex items-center space-x-2">
              <SecurityCameraIcon className="w-6 h-6 text-teal-600"/>
              <span>Overall Score</span>
            </CardTitle>
          </CardHeader>
          <CardContent>
            <div className="flex-items-center space-x-6">
              <div className="relative">
                <div className="w-24 h-24 rounded-full border-8 border-slate-600 flex items-center justify-center">
                  <span className={`${getScoreColor(complianceScore)} text-3xl font-bold`}>{complianceScore}</span>
                </div>
                <div 
                  className={`absolute inset-0 rounded-full border-slate-200 flex items-center justify-center ${
                    complianceScore >= 100 ? 'border-t-green-500 border-r-green-500' :
                    complianceScore >=60 ? 'border-t-orange-500 border-r-orange-500' :
                    'border-t-red-500 border-r-red-500'
                  }`}
                  style = {{
                    transform: `rotate(${complianceScore * 3.6}deg)`,
                    transition: 'transform 0.5s ease-in-out'
                  }}
                />
              </div>
              <div className="flex-1">
                <p className="text-slate-600 mb-2">
                  {
                    complianceScore >= 100 ? 'Compliant' :
                    complianceScore >= 60 ? 'Partially Compliant' :
                    'Non-Compliant'
                  }
                </p>
                <div className="flex-items-center space-x-4 text-sm text-slate-600">
                  <span className="flex items-center space">
                    +5 points this week
                  </span>
                  <span className="flex-items-center space">
                    Last Update: Today
                  </span>
                </div>
              </div>
            </div>
          </CardContent>
        </Card>

        <div className="grid md:grid-cols-2 gap-4 lg:grid-cols-4 gaps-6">
          <Card className="bg-black border-white">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-white flex-items-center">
                <XIcon className="w-4 h-4 mr-2"/>
                Critical Issues 
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">
                {criticalIssues}
              </div>
              <p className="text-xs text-white">Require immediate action</p>
            </CardContent>
          </Card>

          <Card className="bg-red-700 border-black">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-red-300 flex-items-center">
                <XIcon className="w-4 h-4 mr-2"/>
                Critical Issues 
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">
                {criticalIssues}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-red-50 border-black">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-black flex-items-center">
                <XIcon className="w-4 h-4 mr-2"/>
                Critical Issues 
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">
                {criticalIssues}
              </div>
            </CardContent>
          </Card>

          <Card className="bg-red-50 border-black">
            <CardHeader className="pb-3">
              <CardTitle className="text-sm font-medium text-black flex-items-center">
                <XIcon className="w-4 h-4 mr-2"/>
                Critical Issues 
              </CardTitle>
            </CardHeader>
            <CardContent>
              <div className="text-3xl font-bold text-white">
                {criticalIssues}
              </div>
            </CardContent>
          </Card>
        </div>

      </div>  
    </Layout>
  )
};

export default Home;