import React from "react";
// import { NavLink } from "react-router-dom";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { Upload, FileText, House, Wrench, Database} from 'phosphor-react';
import { Icon } from "lucide-react";

const Navbar = () => {

    const pathname = usePathname();

    const navItems = [
        {to: '/', icon: House, label: 'Home'},
        {to: '/upload', icon: Upload, label: 'Upload'},
        {to: '/database', icon: Database, label: 'Database'},
        {to: '/reports', icon: FileText, label: 'Reports'},
        {to: '/settings', icon: Wrench, label: 'Settings'}
    ];

    return (
        <nav className="bg-gray-800">
            <div>
                <div className="flex justify-between items-center h-16">
                    <div className="flex items-center space-x-4">
                        <div className="flex-shrink-0">
                            <h1 className="text-3xl font-bold text-white">
                                Label Lens
                            </h1>
                        </div>
                        <div className="hidden md:block">
                            <div className="flex items-baseline space-x-4">
                                {navItems.map(({to, icon: Icon, label}) => { 
                                    const isActive = pathname === to;
                                    return (
                                      <Link
                                        key={to}
                                        href={to}
                                        className={`flex items-center px-3 py-2 rounded-md text-sm font-medium transition-colors ${
                                            isActive
                                            ? 'bg-gray-900 text-white'
                                            : 'text-gray-300 hover:bg-gray-700 hover:text-white'
                                        }`}
                                      >
                                        <Icon size={20}/>
                                        <span className="ml-2">{label}</span>
                                      </Link>  
                                    );
                                })}
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </nav>
    );
};

export default Navbar