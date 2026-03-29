import React from 'react';
import { 
  UserPlusIcon, 
  EllipsisHorizontalIcon,
  PencilSquareIcon,
  ArrowDownTrayIcon,
  Cog6ToothIcon,
  BoltIcon,
  UserIcon
} from '@heroicons/react/24/outline';

export default function Team() {
  const members = [
    { name: 'Julian Sterling', email: 'julian@lumen.ledger', role: 'Admin', active: '2m ago', status: 'Active', avatar: 'https://ui-avatars.com/api/?name=Julian+Sterling&background=random' },
    { name: 'Elena Vance', email: 'elena.vance@lumina.io', role: 'Member', active: '4h ago', status: 'Active', avatar: 'https://ui-avatars.com/api/?name=Elena+Vance&background=random' },
    { name: 'Marcus Thorne', email: 'm.thorne@partner.com', role: 'Viewer', active: '-', status: 'Invited', avatar: null },
    { name: 'Aaron Kwok', email: 'akwok@lumen.ledger', role: 'Member', active: 'Yesterday', status: 'Active', avatar: 'https://ui-avatars.com/api/?name=Aaron+Kwok&background=random' },
  ];

  const activities = [
    { user: 'Julian Sterling', actionPart1: 'updated the', actionHighlight: 'Marketing budget', time: '2 minutes ago', icon: PencilSquareIcon, color: 'bg-primary-500 text-white' },
    { user: 'Elena Vance', actionPart1: 'invited', actionHighlight: 'Marcus Thorne', actionPart2: 'to the team', time: '3 hours ago', icon: UserPlusIcon, color: 'bg-success-500 text-white' },
    { user: 'Aaron Kwok', actionPart1: 'exported the', actionHighlight: 'Q3 Revenue Report', time: 'Yesterday at 4:12 PM', icon: ArrowDownTrayIcon, color: 'bg-warning-500 text-white' },
    { user: 'Julian Sterling', actionPart1: 'changed team visibility to', actionHighlight: 'Private', time: '2 days ago', icon: Cog6ToothIcon, color: 'bg-neutral-500 text-white' },
  ];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-12 gap-12 lg:gap-16 min-h-screen">
      <div className="lg:col-span-8 space-y-8">
        <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
          <div>
            <h1 className="text-4xl font-extrabold tracking-tight text-neutral-900 mb-2">Team Members</h1>
            <p className="text-neutral-500 text-sm">Manage roles, permissions, and collaboration across your organization.</p>
          </div>
          <button className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-br from-primary-600 to-primary-800 text-white font-medium rounded-xl hover:opacity-90 shadow-lg shadow-primary-600/20 transition-transform active:scale-95">
            <UserPlusIcon className="w-5 h-5" />
            <span>Invite Member</span>
          </button>
        </div>

        <div className="bg-white border text-sm border-neutral-200 rounded-2xl overflow-hidden shadow-sm">
          <div className="overflow-x-auto">
            <table className="w-full text-left border-collapse">
              <thead>
                <tr className="bg-neutral-50/80 text-neutral-500 text-[11px] uppercase tracking-[0.1em] font-bold border-b border-neutral-200">
                  <th className="px-6 py-4">Name</th>
                  <th className="px-6 py-4">Role</th>
                  <th className="px-6 py-4">Last Active</th>
                  <th className="px-6 py-4">Status</th>
                  <th className="px-6 py-4 text-right">Action</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-neutral-100">
                {members.map((member, idx) => (
                  <tr key={idx} className="group hover:bg-neutral-50/50 transition-colors">
                    <td className="px-6 py-6">
                      <div className="flex items-center gap-3">
                        {member.avatar ? (
                          <div className="w-10 h-10 rounded-xl overflow-hidden ring-2 ring-white shadow-sm flex-shrink-0">
                            <img src={member.avatar} alt={member.name} className="w-full h-full object-cover" />
                          </div>
                        ) : (
                          <div className="w-10 h-10 rounded-xl bg-neutral-100 flex items-center justify-center text-neutral-400 ring-2 ring-white shadow-sm flex-shrink-0">
                            <UserIcon className="w-5 h-5" />
                          </div>
                        )}
                        <div>
                          <div className="font-semibold text-neutral-900">{member.name}</div>
                          <div className="text-xs text-neutral-500 mt-0.5">{member.email}</div>
                        </div>
                      </div>
                    </td>
                    <td className="px-6 py-6">
                      <span className="text-xs font-medium px-2 py-1 bg-neutral-100 rounded-md text-neutral-800">
                        {member.role}
                      </span>
                    </td>
                    <td className="px-6 py-5 font-mono text-xs text-neutral-500">
                      {member.active}
                    </td>
                    <td className="px-6 py-6">
                      <div className="flex items-center gap-1.5">
                        <span className={`w-2 h-2 rounded-full ${member.status === 'Active' ? 'bg-success-500' : 'bg-neutral-300'}`}></span>
                        <span className={`text-xs ${member.status === 'Active' ? 'text-neutral-900' : 'text-neutral-500 italic'}`}>
                          {member.status}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-5 text-right">
                      {member.status === 'Invited' ? (
                        <button className="text-[11px] font-bold text-primary-600 uppercase tracking-wider hover:underline">Resend</button>
                      ) : (
                        <button className="p-2 text-neutral-400 hover:text-primary-600 transition-colors">
                          <EllipsisHorizontalIcon className="w-5 h-5" />
                        </button>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>

      <div className="lg:col-span-4 space-y-8">
        <div className="bg-white border border-neutral-200 rounded-3xl p-8 shadow-sm">
          <h2 className="text-lg font-bold text-neutral-900 mb-6 flex items-center gap-2">
            <BoltIcon className="w-5 h-5 text-primary-600 fill-primary-100" />
            Recent Activity
          </h2>
          
          <div className="space-y-8 relative">
            {/* Connecting Line */}
            <div className="absolute left-[11px] top-2 bottom-2 w-px bg-neutral-200/60"></div>
            
            {activities.map((act, idx) => (
              <div key={idx} className="relative flex gap-4 pl-1">
                <div className={`z-10 w-6 h-6 rounded-full ${act.color} flex items-center justify-center ring-4 ring-white`}>
                  <act.icon className="w-3.5 h-3.5 stroke-2" />
                </div>
                <div className="flex-grow pt-0.5">
                  <p className="text-sm leading-relaxed text-neutral-700">
                    <span className="font-bold text-neutral-900">{act.user}</span> {act.actionPart1} <span className="text-primary-600 font-medium">{act.actionHighlight}</span> {act.actionPart2}
                  </p>
                  <span className="block mt-1 text-[10px] font-medium text-neutral-400 uppercase tracking-widest">{act.time}</span>
                </div>
              </div>
            ))}
          </div>
          <button className="w-full mt-8 py-3 text-sm font-semibold text-primary-600 border border-transparent hover:bg-neutral-50 rounded-xl transition-colors">
            View All Activity
          </button>
        </div>

        <div className="bg-gradient-to-br from-white to-neutral-50 border border-neutral-200 rounded-3xl p-8 shadow-sm">
          <h3 className="font-bold text-neutral-900 mb-2">Role Management</h3>
          <p className="text-xs text-neutral-500 leading-relaxed">
            Administrators can manage billing and invite members. Members can view and edit budgets. Viewers are restricted to read-only access.
          </p>
          <div className="mt-4 flex gap-2">
            <div className="w-1.5 h-1.5 rounded-full bg-primary-600"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-neutral-300"></div>
            <div className="w-1.5 h-1.5 rounded-full bg-neutral-300"></div>
          </div>
        </div>
      </div>
    </div>
  );
}
